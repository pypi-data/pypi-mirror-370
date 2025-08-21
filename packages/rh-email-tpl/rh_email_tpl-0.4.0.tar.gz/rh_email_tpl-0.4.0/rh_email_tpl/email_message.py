import logging
import mimetypes
import os
import re
from base64 import b64encode
from pathlib import Path

from django.conf import settings
from django.contrib.staticfiles import finders
from django.core.files.base import ContentFile, File
from django.core.mail.message import EmailMessage, EmailMultiAlternatives
from django.db.models.fields.files import FieldFile
from django.template import engines, loader

from rh_email_tpl.utils.translation import custom_translation_override

logger = logging.getLogger(__name__)


class RHEmailMessage:
    subject = ""
    template_html = ""
    template_text = ""
    generate_text_from_html = False
    email_multi_alternatives_class = EmailMultiAlternatives
    reply_to = []
    sender_display_label = None

    def __init__(
        self,
        subject="",
        template_html="",
        template_text="",
        generate_text_from_html=False,
        context=None,
        from_email=None,
        to=None,
        cc=None,
        bcc=None,
        reply_to=None,
        attached_files=None,
        extra_email_kwargs=None,
        sender_display_label=None,
        *args,
        **kwargs,
    ):
        if args:
            logger.warning(
                "Received unsupported args: %s",
                args,
                extra={"args": args},  # noqa: G101
            )
        if kwargs:
            logger.warning(
                "Received unsupported kwargs: %s",
                kwargs,
                extra={"kwargs": kwargs},
            )

        self.subject = self.subject or subject
        self.template_html = template_html or self.template_html
        self.template_text = template_text or self.template_text
        self.generate_text_from_html = (
            self.generate_text_from_html or generate_text_from_html
        )
        self.context = context
        self.from_email = from_email
        self.to = to
        self.cc = cc
        self.bcc = bcc
        self.reply_to = reply_to
        self.attached_files = attached_files
        self.extra_email_kwargs = extra_email_kwargs
        self.sender_display_label = sender_display_label

    def get_context_data(self):
        return self.context or {}

    def get_from_email(self):
        if not self.from_email:
            raise NotImplementedError
        return self.from_email

    def get_to(self):
        if not self.to:
            raise NotImplementedError
        return self.to

    def get_cc(self):
        return self.cc or []

    def get_bcc(self):
        return self.bcc or []

    def get_reply_to(self):
        return self.reply_to or []

    def get_attached_files(self):
        return self.attached_files or []

    def get_subject(self):
        return self.subject

    def get_sender_display_label(self):
        return self.sender_display_label

    def get_final_from_email(self):
        sender_display_label = self.get_sender_display_label()
        from_email = self.get_from_email()
        if sender_display_label:
            return f"{sender_display_label} <{from_email}>"
        return from_email

    def get_template_html(self):
        return self.template_html

    def get_template_text(self):
        return self.template_text

    def get_generate_text_from_html(self):
        return self.generate_text_from_html

    def get_body_html(self, replace_cid_urls=False):
        html = loader.get_template(self.get_template_html()).render(
            self.get_context_data(),
        )

        if replace_cid_urls:
            html = html.replace("cid:", "")

        return html

    def get_body_text(self):
        context = self.get_context_data()
        if self.get_generate_text_from_html():
            context["__text_output__"] = True
            html_template = loader.get_template(self.get_template_html()).template
            template = engines["django"].from_string(
                html_template.source.replace(".html", ".txt"),
            )
            del context[
                "__text_output__"
            ]  # unset the flag afterwards to avoid strange side-effects
        else:
            template = loader.get_template(self.get_template_text())

        text = template.render(context)
        return self.clean_up_body_text(text)

    def clean_up_body_text(self, text):
        text = text.replace("\r", "")

        # replace double spaces by single one
        while "  " in text:
            text = text.replace("  ", " ")

        # remove lines with only one space
        while "\n \n" in text:
            text = text.replace("\n \n", "\n\n")

        # replace multiple empty lines by single one
        while "\n\n\n" in text:
            text = text.replace("\n\n\n", "\n\n")

        # Transform <a href="http://example.com">Link Content</a> => Link Content: http://example.com
        # But skip <a href="http://example.com">http://example.com</a>
        text = re.sub(r"<a href=\"([^\"]+)\"[^>]*>(?!http)([^<]+)</a>", r"\2: \1", text)

        text = re.sub(r"__LINEBREAK__", "\n", text)
        text = re.sub(r"<br.*?>", "\n", text)
        text = re.sub(r"<.*?>", "", text)
        text = text.replace("\n", "\r\n")
        return text.strip()

    def get_image_path(self, image_file):
        # handle /media/ urls
        if image_file.startswith(settings.MEDIA_URL):
            directory, filename = os.path.split(image_file)
            directory = str(
                Path(
                    settings.MEDIA_ROOT,
                    directory[len(settings.MEDIA_URL) :],
                ),
            )
        # all other images taken from static root
        else:
            directory, filename = os.path.split(image_file)
            result = finders.find("/".join(directory.split("/")[2:]))
            if result:
                if isinstance(result, list):
                    result = result[0]
                directory = result
            else:
                logger.warning("Was unable to find static file %s", image_file)
        return str(Path(directory, filename))

    def _process_html_body(self, msg):
        body_html = self.get_body_html()
        image_files = set(re.findall(r'cid:([^"\']+)', body_html))
        for image_file in image_files:
            b64_image_file = b64encode(image_file.encode("utf-8")).decode("utf-8")
            # add image and replace cid with base64 alias
            msg.attach_inline_image(
                filepath=self.get_image_path(image_file),
                cid=b64_image_file,
            )
            body_html = body_html.replace(
                f"cid:{image_file}",
                f"cid:{b64_image_file}",
            )
        msg.attach_alternative(body_html, "text/html")

    def get_extra_email_kwargs(self):
        """
        Pass extra kwargs to email_multi_alternatives_class initialisation
        """
        return self.extra_email_kwargs or {}

    def pre_send(self):
        """
        Called before sending email, if validation is needed as an example
        """
        return

    @custom_translation_override("de")
    def send_email(self):
        self.pre_send()

        msg = self.email_multi_alternatives_class(
            subject=self.get_subject(),
            body=self.get_body_text(),
            from_email=self.get_final_from_email(),
            to=self._clean_address_list(self.get_to()),
            cc=self._clean_address_list(self.get_cc()),
            bcc=self._clean_address_list(self.get_bcc()),
            reply_to=self._clean_address_list(self.get_reply_to()),
            **self.get_extra_email_kwargs(),
        )
        self._process_html_body(msg)
        self.add_attachments(msg)

        msg.send()

    def add_attachments(self, email_message):
        for _file in self.get_attached_files():
            if isinstance(_file, str):
                with Path(_file).open(mode="rb") as f:
                    self.add_attachment(f, email_message)
            else:
                self.add_attachment(_file, email_message)

    def add_attachment(self, _file: File, email_message: EmailMessage):
        content_type, encoding = mimetypes.guess_type(_file.name)
        email_message.attach(Path(_file.name).name, _file.read(), content_type)

    def add_attachment_by_filename(
        self,
        email_message: EmailMessage,
        filename: str,
        description: str,
    ):
        try:
            with Path(filename).open(mode="rb") as attachment_file:
                attachment = File(file=attachment_file, name=description)
                self.add_attachment(attachment, email_message)
        except OSError:
            if settings.DEBUG:
                logger.error("file not found to attach: %s", filename)
            else:
                raise

    def add_attachment_by_content(
        self,
        email_message: EmailMessage,
        content: str,
        description: str,
    ):
        attachment = ContentFile(content=content, name=description)
        self.add_attachment(attachment, email_message)

    def add_attachment_by_fieldfile(self, email_message, fieldfile, description=None):
        if not isinstance(fieldfile, FieldFile):
            raise AssertionError

        if description is None:
            description = fieldfile.name
        self.add_attachment_by_filename(
            email_message=email_message,
            filename=fieldfile.path,
            description=description,
        )

    def send(self):
        return self.send_email()

    def _clean_address_list(self, _list):
        if not isinstance(_list, list | tuple | set):
            raise ValueError("addresses must be provided as list, tuple or set")
        return _list and [e for e in set(_list) if e]
