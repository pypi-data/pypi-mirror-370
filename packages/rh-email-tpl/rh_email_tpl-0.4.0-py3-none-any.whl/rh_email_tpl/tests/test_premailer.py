from pathlib import Path

import django
from django.conf import settings
from django.template import Context
from django.template.loader import get_template
from django.test import TestCase
from django.test.utils import override_settings
from lxml import html
from lxml.sax import etree

# based on https://github.com/alexhayes/django-premailer/blob/master/django_premailer/templatetags/premailer.py
# which is not maintained anymore

TESTS_TEMPLATE_DIR = str(Path(__file__).parent.joinpath("premailer_templates"))
TEMPLATES = settings.TEMPLATES
TEMPLATES[0]["DIRS"].append(TESTS_TEMPLATE_DIR)


@override_settings(TEMPLATES=TEMPLATES)
class PremailerTests(TestCase):
    def pretty(self, ugly):
        """
        Force a HTML document to be made pretty.
        NOTE: This method is required because of strange differences
        in the way premailer/lxml makes decisions about
        the placement of newlines. Using tox all tests pass without this hack,
        however in travis and circleci the
        :py:meth:`.PremailerTests.test_basic` test fails due to some
        missing ``\n`` in the generated ``actual`` HTML.
        """
        document_root = html.fromstring(
            ugly.replace("\n", "").replace("\t", "").replace("  ", ""),
        )
        return etree.tostring(document_root, encoding="unicode", pretty_print=True)

    def assert_expected(self, actual, expected):
        with Path(TESTS_TEMPLATE_DIR, expected).open(encoding="utf-8") as f:
            expected = f.read()
            self.assertEqual(self.pretty(actual), self.pretty(expected))

    def test_basic(self):
        """
        A very basic test that ensures the tag does what we expect it to do.
        """
        template = get_template("basic.html")
        context = Context({"eggs": "Sausage"})
        if django.VERSION >= (1, 8):
            context = context.flatten()
        rendered = template.render(context)
        self.assert_expected(rendered, "basic.expected.html")

    def test_basic_base_url(self):
        """
        Override the base_url.
        """
        template = get_template("basic-base-url.html")
        context = Context({"eggs": "Sausage"})
        if django.VERSION >= (1, 8):
            context = context.flatten()
        rendered = template.render(context)
        self.assert_expected(rendered, "basic-base-url.expected.html")
