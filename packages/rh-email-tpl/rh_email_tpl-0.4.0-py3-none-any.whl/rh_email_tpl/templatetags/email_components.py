import logging

from django import template as dj_template
from django.template import loader
from django.template.base import FilterExpression, Variable
from django.template.defaulttags import token_kwargs

logger = logging.getLogger(__name__)
register = dj_template.Library()


def generate_block_tag(parser, token, tag_class, endtag, **kwargs):
    """Factory for creating tags."""
    bits = token.split_contents()
    extra_context = token_kwargs(bits[1:], parser)
    nodelist = parser.parse((endtag,))
    parser.delete_first_token()
    return tag_class(nodelist, extra_context, **kwargs)


class EmailBlockTag(dj_template.Node):
    """
    Node for rendering a meta element which doesn't have it's own text
    representation but uses the one from the contained elements.

    Acts as a block and assigns the content of the block to the value of
    ``CONTEXT_VAR_CONTENT`` in the context of the underlying template.

    Additional context variables can be added that will be used when rendering
    the _underlying template_, this will influence the context of the block!

    For example, given a underlying template of::

        <p class='{{ color }}'>{{ text }}</p>

    And the main context has template variable color='blue', the following::

        {% emailparagraph color='red' %}
            The car is {{ color }}.
        {% endemailparagraph %}

    Will render as::

        <p class='red'>The car is blue.</p>
    """

    # This is what the content of the block will be referred to as in the
    # underlying template.
    CONTEXT_VAR_CONTENT = "text"

    def __init__(self, nodelist, extra_context, template_html=None):
        self.extra_context = extra_context
        self.template_html = template_html
        self.nodelist = nodelist

    def render(self, context):
        template = self.get_template(context)
        content = self.nodelist.render(context)
        values = self.parse_context(context, content)

        with context.push(values):
            return template.render(context.flatten())

    def get_template(self, context):
        return loader.get_template(self.template_html)

    def _resolve_var(self, var, context):
        """
        Workaround for some variables being already resolved.
        """
        if not isinstance(var, FilterExpression | Variable):
            return var
        return var.resolve(context)

    def parse_context(self, context, content=None):
        content = content or ""
        values = {
            key: self._resolve_var(val, context)
            for key, val in self.extra_context.items()
        }
        values[self.CONTEXT_VAR_CONTENT] = self.clean_content(content)
        return values

    def clean_content(self, content):
        """
        Remove all unnecessary whitespace and newlines from content.
        """
        return " ".join(content.split())


class EmailTextHtmlBlockTag(EmailBlockTag):
    """
    Same as EmailBlockTag but will automatically generate a text version using the
    template_text template file.
    """

    TEMPLATE_HTML = None  # required
    TEMPLATE_TEXT = None  # not required

    # This context variable determines if the text or HTML version
    # will be rendered.
    CONTEXT_VAR_TEXT = "__text_output__"

    def __init__(
        self,
        nodelist,
        extra_context=None,
        template_html=None,
        template_text=None,
    ):
        super().__init__(
            nodelist=nodelist,
            extra_context=extra_context,
            template_html=template_html,
        )
        self.template_text = template_text or self.TEMPLATE_TEXT

    def render(self, context):
        template = self.get_template(context)
        content = self.nodelist.render(context)
        values = self.parse_context(context, content)

        with context.push(values):
            return template.render(context.flatten())

    def get_template(self, context):
        """
        Get the underlying template to use based on what the CONTEXT_VAR_TEXT
        context variable is set to.

        The TEMPLATE_HTML class constant is required, the TEMPLATE_TEXT class
        constant is optional. If TEMPLATE_TEXT is not set, it is assumed that
        the html file's extension can just be changed from .html to .txt
        """
        if not self.is_txt_version(context):
            template_filename = self.template_html
        elif self.template_text:
            template_filename = self.template_text
        else:
            template_filename = self.template_html.replace(".html", ".txt")
        return loader.get_template(template_filename)

    def is_txt_version(self, context):
        return context.get(self.CONTEXT_VAR_TEXT, False)


class EmailTextHtmlPreserveWhitespaceBlockTag(EmailTextHtmlBlockTag):
    """
    Same as EmailTextHtmlBlockTag, but doesn't remove whitespace from content.
    """

    def clean_content(self, content):
        return content


# base components as building bricks for emails and meta components


@register.tag("emailheader")
def do_email_header(parser, token):
    """
    header of the email containing company logos

    {% emailheader %}{% endemailheader %}
    """
    return generate_block_tag(
        parser,
        token,
        EmailTextHtmlBlockTag,
        "endemailheader",
        template_html="email/som/tags/header.html",
    )


@register.tag("emailfooter")
def do_email_footer(parser, token):
    """
    footer of the email containing imprint and legal information

    {% emailfooter %}{% endemailfooter %}
    """
    return generate_block_tag(
        parser,
        token,
        EmailTextHtmlBlockTag,
        "endemailfooter",
        template_html="email/som/tags/footer.html",
    )


@register.tag("emailcontent")
def do_email_content(parser, token):
    """
    content area with grey background

    {% emailcontent %}
      Some other content, may be text or additional elements
    {% endemailcontent %}
    """
    return generate_block_tag(
        parser,
        token,
        EmailTextHtmlPreserveWhitespaceBlockTag,
        "endemailcontent",
        template_html="email/som/tags/content.html",
    )


@register.tag("emailunsubscribe")
def do_email_unsubscribe(parser, token):
    """
    part of the email containing the unsubscribe possibility

    {% emailunsubscribe %}{% endemailunsubscribe %}
    """
    return generate_block_tag(
        parser,
        token,
        EmailTextHtmlBlockTag,
        "endemailunsubscribe",
        template_html="email/som/tags/unsubscribe.html",
    )


@register.tag("emailparagraph")
def do_email_paragraph(parser, token):
    """
    paragraph with bottom margin

    {% emailparagraph %}
      Some other content, may be text or additional elements
    {% endemailparagraph %}
    """
    return generate_block_tag(
        parser,
        token,
        EmailTextHtmlBlockTag,
        "endemailparagraph",
        template_html="email/som/tags/paragraph.html",
    )


@register.tag("emailsmall")
def do_email_small(parser, token):
    """
    small text

    {% emailsmall %}
      Some small content, may be text or additional elements
    {% endemailsmall %}
    """
    return generate_block_tag(
        parser,
        token,
        EmailTextHtmlBlockTag,
        "endemailsmall",
        template_html="email/som/tags/small.html",
    )


@register.tag("emailmedium")
def do_email_medium(parser, token):
    """
    medium sized text

    {% emailmedium %}
      Some medium sized content, may be text or additional elements
    {% endemailmedium %}
    """
    return generate_block_tag(
        parser,
        token,
        EmailTextHtmlBlockTag,
        "endemailmedium",
        template_html="email/som/tags/medium.html",
    )


@register.tag("emailcenter")
def do_email_center(parser, token):
    """
    centered content

    {% emailcenter %}
      Some centered content, may be text or additional elements
    {% endemailcenter %}
    """
    return generate_block_tag(
        parser,
        token,
        EmailTextHtmlBlockTag,
        "endemailcenter",
        template_html="email/som/tags/center.html",
    )


@register.tag("emailheading")
def do_email_heading(parser, token):
    """
    orange heading

    {% emailheading %}This is my heading text {% endemailheading %}
    """
    return generate_block_tag(
        parser,
        token,
        EmailTextHtmlBlockTag,
        "endemailheading",
        template_html="email/som/tags/heading.html",
    )


@register.tag("emailsectionheadline")
def do_email_section_headline(parser, token):
    """
    section headline

    {% emailsectionheadline %}This is a headline{% endemailsectionheadline %}
    """
    return generate_block_tag(
        parser,
        token,
        EmailTextHtmlBlockTag,
        "endemailsectionheadline",
        template_html="email/som/tags/section_headline.html",
    )


@register.tag("emailsection")
def do_email_section(parser, token):
    """
    section devider (with optional leading image)

    {% emailsection %}This is a section{% endemailsection %}

    Accepted arguments:
        image (optional) - path to the static image file
    """
    return generate_block_tag(
        parser,
        token,
        EmailTextHtmlBlockTag,
        "endemailsection",
        template_html="email/som/tags/section.html",
    )


@register.tag("emaileyecatcher")
def do_email_eyecatcher(parser, token):
    """
    orange eye catcher element (with optional leading image and subline)

    {% emaileyecatcher
       image="img/email/som/eyecatcher_impressions.png"
       subline="Awesome subline text" %}
        This is an eyecatcher
    {% endemaileyecatcher %}

    Accepted arguments:
        image (optional) - path to the static image file
        subline (optional) - text shown below the eyecatcher heading
    """
    return generate_block_tag(
        parser,
        token,
        EmailTextHtmlBlockTag,
        "endemaileyecatcher",
        template_html="email/som/tags/eyecatcher.html",
    )


@register.tag("emailserviceemployee")
def do_email_service_employee(parser, token):
    """
    service employee image and contact component

    Accepts arguments:
        service_employee (required) - user instance of the service employee
    """
    return generate_block_tag(
        parser,
        token,
        EmailTextHtmlBlockTag,
        "endemailserviceemployee",
        template_html="email/som/tags/service_employee.html",
    )


@register.tag("emailbutton")
def do_email_button(parser, token):
    """
    an action button with a target url and text

    Accepted arguments:
        link (required) - target url to link to
    """
    return generate_block_tag(
        parser,
        token,
        EmailTextHtmlBlockTag,
        "endemailbutton",
        template_html="email/som/tags/button.html",
    )


@register.tag("emailstripline")
def do_email_stripline(parser, token):
    """
    horizontal divider line
    """
    return generate_block_tag(
        parser,
        token,
        EmailTextHtmlBlockTag,
        "endemailstripline",
        template_html="email/som/tags/stripline.html",
    )


@register.tag("emaillist")
def do_email_list(parser, token):
    """
    list container to render emaillistitem elements

    Accepts arguments:
        ordered (optional, default: False) - define if it should be an ordered
          or unordered list
        padding (optional, default: 0) - element padding
    """
    return generate_block_tag(
        parser,
        token,
        EmailTextHtmlBlockTag,
        "endemaillist",
        template_html="email/som/tags/list.html",
    )


@register.tag("emaillistitem")
def do_email_listitem(parser, token):
    """
    list item

    Accepts arguments:
        bullet_color (optional, default: inherit) - color of the bullet point)
    """
    return generate_block_tag(
        parser,
        token,
        EmailTextHtmlBlockTag,
        "endemaillistitem",
        template_html="email/som/tags/list_item.html",
    )


@register.tag("emailcolor")
def do_email_color(parser, token):
    """
    colored text

    Accepts arguments:
        color (required) - hex code of color with leading hash
    """
    return generate_block_tag(
        parser,
        token,
        EmailTextHtmlBlockTag,
        "endemailcolor",
        template_html="email/som/tags/color.html",
    )


@register.tag("emailbold")
def do_email_bold(parser, token):
    """
    bold formatted text
    """
    return generate_block_tag(
        parser,
        token,
        EmailTextHtmlBlockTag,
        "endemailbold",
        template_html="email/som/tags/bold.html",
    )


@register.tag("emailitalic")
def do_email_italic(parser, token):
    """
    italic text
    """
    return generate_block_tag(
        parser,
        token,
        EmailTextHtmlBlockTag,
        "endemailitalic",
        template_html="email/som/tags/italic.html",
    )


@register.tag("emailwarning")
def do_email_warning(parser, token):
    """
    warning message with leading warning sign image
    """
    return generate_block_tag(
        parser,
        token,
        EmailTextHtmlBlockTag,
        "endemailwarning",
        template_html="email/som/tags/warning.html",
    )


@register.tag("emailtable")
def do_email_table(parser, token):
    """
    table base element that should contain extaclty one of emailtable_thead
    and/or emailtable_tbody element
    """
    return generate_block_tag(
        parser,
        token,
        EmailTextHtmlBlockTag,
        "endemailtable",
        template_html="email/som/tags/table.html",
    )


@register.tag("emailtable_noborder")
def do_email_table_noborder(parser, token):
    """
    table base element that should contain extaclty one of emailtable_thead
    and/or emailtable_tbody element
    """
    return generate_block_tag(
        parser,
        token,
        EmailTextHtmlBlockTag,
        "endemailtable_noborder",
        template_html="email/som/tags/table_noborder.html",
    )


@register.tag("emailtable_thead")
def do_email_table_thead(parser, token):
    """
    table header container that should contain exactly one emailtable_tr element
    """
    return generate_block_tag(
        parser,
        token,
        EmailTextHtmlBlockTag,
        "endemailtable_thead",
        template_html="email/som/tags/table_thead.html",
    )


@register.tag("emailtable_tbody")
def do_email_table_tbody(parser, token):
    """
    table body container that should contain one or more emailtable_tr elements
    """
    return generate_block_tag(
        parser,
        token,
        EmailTextHtmlBlockTag,
        "endemailtable_tbody",
        template_html="email/som/tags/table_tbody.html",
    )


@register.tag("emailtable_tr")
def do_email_table_tr(parser, token):
    """
    table row container that should contain one or more emailtable_td cell elements
    """
    return generate_block_tag(
        parser,
        token,
        EmailTextHtmlBlockTag,
        "endemailtable_tr",
        template_html="email/som/tags/table_tr.html",
    )


@register.tag("emailtable_th")
def do_email_table_th(parser, token):
    """
    a table header cell element
    """
    return generate_block_tag(
        parser,
        token,
        EmailTextHtmlBlockTag,
        "endemailtable_th",
        template_html="email/som/tags/table_th.html",
    )


@register.tag("emailtable_td")
def do_email_table_td(parser, token):
    """
    a regular table cell element
    """
    return generate_block_tag(
        parser,
        token,
        EmailTextHtmlBlockTag,
        "endemailtable_td",
        template_html="email/som/tags/table_td.html",
    )


@register.tag("emaillinebreak")
def do_email_linebreak(parser, token):
    """
    line break
    """
    return generate_block_tag(
        parser,
        token,
        EmailTextHtmlBlockTag,
        "endemaillinebreak",
        template_html="email/som/tags/line_break.html",
    )


@register.tag("emaillink")
def do_email_link(parser, token):
    """
    link

    Accepts arguments:
        placeholder (optional) - an alternative text version
        protocol (optional) - mailto|tel etc., used to hide these protocols in
          the text variant
        remove_underline
    """
    return generate_block_tag(
        parser,
        token,
        EmailTextHtmlBlockTag,
        "endemaillink",
        template_html="email/som/tags/link.html",
    )


@register.tag("emailnowrap")
def do_email_nowrap(parser, token):
    """
    make content non-wrappable
    """
    return generate_block_tag(
        parser,
        token,
        EmailTextHtmlBlockTag,
        "endemailnowrap",
        template_html="email/som/tags/nowrap.html",
    )


@register.tag("emailcode")
def do_email_code(parser, token):
    """
    display code in a proper way
    """
    return generate_block_tag(
        parser,
        token,
        EmailTextHtmlPreserveWhitespaceBlockTag,
        "endemailcode",
        template_html="email/som/tags/code.html",
    )


@register.tag("emailpre")
def do_email_pre(parser, token):
    """
    preformatted text
    """
    return generate_block_tag(
        parser,
        token,
        EmailTextHtmlPreserveWhitespaceBlockTag,
        "endemailpre",
        template_html="email/som/tags/pre.html",
    )


@register.tag("emaildel")
def do_email_del(parser, token):
    """
    deleted text.

    {% emaildel %}
      Some small content, may be text or additional elements
    {% endemaildel %}
    """
    return generate_block_tag(
        parser,
        token,
        EmailTextHtmlBlockTag,
        "endemaildel",
        template_html="email/som/tags/del.html",
    )


@register.tag("emailhtmlescape")
def do_email_html_escape(parser, token):
    """
    raw html that is properly encoded
    """
    return generate_block_tag(
        parser,
        token,
        EmailTextHtmlPreserveWhitespaceBlockTag,
        "endemailhtmlescape",
        template_html="email/som/tags/html_escape.html",
    )


@register.tag("emailcolorpreview")
def do_email_color_preview(parser, token):
    """
    color preview.

    Accepts arguments:
        color (required) - the color to preview
        placeholder (optional) - an alternative text representation
    """
    return generate_block_tag(
        parser,
        token,
        EmailTextHtmlBlockTag,
        "endemailcolorpreview",
        template_html="email/som/tags/color_preview.html",
    )


@register.tag("emailspacer")
def do_email_spacer(parser, token):
    """
    add some space between other elements
    """
    return generate_block_tag(
        parser,
        token,
        EmailTextHtmlBlockTag,
        "endemailspacer",
        template_html="email/som/tags/spacer.html",
    )


@register.tag("emailimage")
def do_email_image(parser, token):
    """
    Block tag for rendering an image. Block contents are used for image URL.

    Accepts arguments:
        alt_text
        width
    """
    return generate_block_tag(
        parser,
        token,
        EmailTextHtmlBlockTag,
        "endemailimage",
        template_html="email/som/tags/image.html",
    )


@register.tag("emailstarrating")
def do_email_star_rating(parser, token):
    """
    Star rating

    Accepts arguments:
        score
    """
    return generate_block_tag(
        parser,
        token,
        EmailTextHtmlBlockTag,
        "endemailstarrating",
        template_html="email/som/tags/star_rating.html",
    )


@register.tag("emailstar")
def do_email_star(parser, token):
    """
    Star

    Accepts arguments:
        color
        size_px
    """
    return generate_block_tag(
        parser,
        token,
        EmailTextHtmlBlockTag,
        "endemailstar",
        template_html="email/som/tags/star.html",
    )


# META components built from other components


@register.tag("emailsalutation")
def do_email_salutation(parser, token):
    """
    closing salutation

    Accepts arguments:
        service_employee (optional) - user instance of the service employee,
          will fall back to generic salutation
    """
    return generate_block_tag(
        parser,
        token,
        EmailBlockTag,
        "endemailsalutation",
        template_html="email/som/tags/meta/salutation.html",
    )
