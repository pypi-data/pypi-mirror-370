import sys

from django import template
from django.conf import settings
from premailer import Premailer

# based on https://github.com/alexhayes/django-premailer/blob/master/django_premailer/templatetags/premailer.py
# which is not maintained anymore

register = template.Library()

PREMAILER_OPTIONS = getattr(settings, "PREMAILER_OPTIONS", {})


class PremailerNode(template.Node):
    def __init__(self, nodelist, filter_expressions):
        self.nodelist = nodelist
        self.filter_expressions = filter_expressions

    def render(self, context):
        rendered_contents = self.nodelist.render(context)
        kwargs = {
            "include_star_selectors": True,
            "cssutils_logging_level": "CRITICAL",
        }

        if "test" in sys.argv:
            kwargs["base_url"] = "http://example.com"

        for expression in self.filter_expressions:
            kwargs.update(base_url=expression.resolve(context, True))

        return Premailer(rendered_contents, **kwargs).transform()


@register.tag
def premailer(parser, token):
    nodelist = parser.parse(("endpremailer",))

    # prevent second parsing of endpremailer
    parser.delete_first_token()

    args = token.split_contents()[1:]

    return PremailerNode(nodelist, [parser.compile_filter(arg) for arg in args])
