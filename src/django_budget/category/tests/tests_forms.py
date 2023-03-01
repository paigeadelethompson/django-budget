from __future__ import unicode_literals

from django.test import TestCase


class CategoryFormTest(TestCase):

    def test_category_form_should_fail_if_data_is_empty(self):
        from category.forms import CategoryForm

        form = CategoryForm(data={})
        self.assertFalse(form.is_valid())

    def test_category_form_slug_field(self):
        from category.forms import CategoryForm

        form = CategoryForm(data={'name': 'Foo Bar'})
        form.is_valid()
        form.save()
        self.assertEqual('foo-bar', form.instance.slug)
