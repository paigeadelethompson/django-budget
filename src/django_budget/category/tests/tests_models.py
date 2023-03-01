from __future__ import unicode_literals

from django.core.urlresolvers import reverse
from django.test import TestCase

from model_mommy import mommy


class CategoryModelTest(TestCase):

    def test_create_new_category(self):
        category = mommy.make('Category')

        self.assertTrue(category.name)
        self.assertTrue(category.slug)

    def test_category_absolute_url(self):
        category = mommy.make('Category')
        url = reverse('category:category_edit', kwargs={'slug': category.slug})

        self.assertEqual(url, category.get_absolute_url())

    def test_delete_category(self):
        category = mommy.make('Category')

        self.assertFalse(category.is_deleted)

        category.delete()

        self.assertTrue(category.is_deleted)

    def test_category_unicode_string(self):
        category = mommy.make('Category', name='Foo')

        self.assertEqual('Foo', str(category))

    def test_category_active_manager(self):
        from category.models import Category

        mommy.make(Category, is_deleted=True)

        self.assertEqual(1, Category.objects.count())
        self.assertEqual(0, Category.active.count())
