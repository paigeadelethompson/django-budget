from __future__ import unicode_literals

from decimal import Decimal

from django.core.urlresolvers import reverse
from django.http import HttpRequest
from django.test import TestCase


class TagNavActiveTestCase(TestCase):

    def setUp(self):
        from base.templatetags.active_tags import navactive

        self.tag = navactive
        self.request = HttpRequest()
        self.context = {'request': self.request}

    def test_tag_should_return_default_css_class(self):
        url = reverse('index')
        self.request.path = url

        self.assertEqual('active', self.tag(self.context, 'index'))

    def test_tag_should_return_empty_string(self):
        self.request.path = '/foo/'

        self.assertEqual('', self.tag(self.context, 'index'))

    def test_tag_should_return_custom_css_class(self):
        url = reverse('index')
        self.request.path = url
        css_class = 'foobar'

        self.assertEqual(css_class, self.tag(self.context, 'index', css_class=css_class))

    def test_tag_should_success_even_url_not_exists(self):
        self.request.path = 'bar'

        self.assertEqual('', self.tag(self.context, 'foo'))


class TagPaginationActiveTestCase(TestCase):

    def setUp(self):
        from base.templatetags.active_tags import pagactive

        self.tag = pagactive
        self.request = HttpRequest()
        self.context = {'request': self.request}

    def test_tag_page_in_request_should_return_default_css_class(self):
        self.request.GET.setdefault('page', '2')
        self.assertEqual('active', self.tag(self.context, 2))

    def test_tag_with_no_page_in_request_should_return_empty_string(self):
        self.assertEqual('', self.tag(self.context, 1))


class TagColarizeAmountTestCase(TestCase):

    def setUp(self):
        from base.templatetags.budget_tags import colorize_amount

        self.tag = colorize_amount

    def test_tag_should_return_empty(self):
        self.assertEqual('', self.tag(Decimal('0'), Decimal('1')))
        self.assertEqual('', self.tag(Decimal('0'), Decimal('0')))

    def test_tag_should_return_danger(self):
        self.assertEqual('danger', self.tag(Decimal('100'), Decimal('100')))
        self.assertEqual('danger', self.tag(Decimal('100'), Decimal('150')))

    def test_tag_should_return_warning(self):
        self.assertEqual('warning', self.tag(Decimal('100'), Decimal('75')))
        self.assertEqual('warning', self.tag(Decimal('100'), Decimal('99.99')))

    def test_tag_should_return_success(self):
        self.assertEqual('success', self.tag(Decimal('100'), Decimal('74')))
        self.assertEqual('success', self.tag(Decimal('100'), Decimal('0')))

    def test_tag_make_decimal(self):
        from base.templatetags.budget_tags import make_decimal

        self.assertEqual(Decimal('1'), make_decimal(1))
        self.assertEqual(Decimal('1'), make_decimal('1'))
        self.assertEqual(Decimal('1'), make_decimal(Decimal('1')))
        self.assertEqual(Decimal('1'), make_decimal(float(1)))
