from __future__ import unicode_literals

from django.contrib import messages
from django.contrib.messages.middleware import MessageMiddleware
from django.contrib.sessions.middleware import SessionMiddleware
from django.core.paginator import Page, Paginator
from django.core.urlresolvers import reverse

from djet.testcases import MiddlewareType
from model_mommy import mommy

from base.utils import BaseTestCase


class CategoryListViewTest(BaseTestCase):
    from category.views import CategoryListView

    url = reverse('category:category_list')
    view_class = CategoryListView

    def test_view_with_no_category(self):
        response = self.get()

        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(response, 'category/list.html')
        self.assertIsInstance(response.context_data['paginator'], Paginator)
        self.assertIsInstance(response.context_data['page_obj'], Page)
        self.assertFalse(response.context_data['is_paginated'])
        self.assertEqual(0, response.context_data['categories'].count())

    def test_view_with_no_active_category(self):
        mommy.make('Category', is_deleted=True)
        response = self.get()

        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(response, 'category/list.html')
        self.assertIsInstance(response.context_data['paginator'], Paginator)
        self.assertIsInstance(response.context_data['page_obj'], Page)
        self.assertFalse(response.context_data['is_paginated'])
        self.assertEqual(0, response.context_data['categories'].count())

    def test_view_with_a_active_category(self):
        category = mommy.make('Category')
        response = self.get()

        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(response, 'category/list.html')
        self.assertIsInstance(response.context_data['paginator'], Paginator)
        self.assertIsInstance(response.context_data['page_obj'], Page)
        self.assertFalse(response.context_data['is_paginated'])
        self.assertEqual(1, response.context_data['categories'].count())
        self.assertIn(category, response.context_data['categories'])

    def test_view_pagination(self):
        mommy.make('Category', _quantity=10)
        category = mommy.make('Category')
        url = '%s?page=2' % self.url
        request = self.factory.get(path=url, user=self.mock_user)
        response = self.view(request)
        response.render()

        self.assertIsInstance(response.context_data['paginator'], Paginator)
        self.assertIsInstance(response.context_data['page_obj'], Page)
        self.assertTrue(response.context_data['is_paginated'])
        self.assertEqual(1, response.context_data['categories'].count())
        self.assertIn(category, response.context_data['categories'])

    def test_html_content_with_no_category(self):
        response = self.get()

        self.assertNotContains(response, 'INVALID VARIABLE:')
        self.assertContains(response, 'Category List', count=2)
        self.assertContains(response, 'New Category')
        self.assertContains(response, reverse('category:category_add'))
        self.assertContains(response, 'No categories found.')

    def test_html_content_with_a_category(self):
        category = mommy.make('Category')
        response = self.get()

        self.assertNotContains(response, 'INVALID VARIABLE:')
        self.assertContains(response, 'Category List', count=2)
        self.assertContains(response, 'New Category')
        self.assertNotContains(response, 'No categories found.')
        self.assertContains(response, category.id)
        self.assertContains(response, category.name)
        self.assertContains(response, reverse('category:category_edit', kwargs={'slug': category.slug}))
        self.assertContains(response, reverse('category:category_delete', kwargs={'slug': category.slug}))

    def test_view_redirect_if_anonymous(self):
        request = self.factory.get(path=self.url, user=self.anonymous_user)
        response = self.view(request)

        self.assertEqual(302, response.status_code)
        self.assertEqual('%s?next=%s' % (reverse('login'), self.url), response._headers['location'][1])

    def get(self):
        request = self.factory.get(path=self.url, user=self.mock_user)
        response = self.view(request)
        return response.render()


class CategoryAddViewTest(BaseTestCase):
    from category.views import CategoryCreateView

    url = reverse('category:category_add')
    view_class = CategoryCreateView

    middleware_classes = [
        SessionMiddleware,
        (MessageMiddleware, MiddlewareType.PROCESS_REQUEST),
    ]

    def test_has_form_on_context(self):
        from category.forms import CategoryForm

        response = self.get()

        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(response, 'category/add.html')
        self.assertIsInstance(response.context_data['form'], CategoryForm)

    def test_show_form_with_errors(self):
        _, response = self.post({})
        response.render()
        form = response.context_data['form']

        self.assertEqual(1, len(form.errors))
        self.assertTrue(form['name'].errors)

    def test_redirect_after_save(self):
        form_data = {'name': 'foo'}
        _, response = self.post(form_data)

        self.assertEqual(302, response.status_code)
        self.assertEqual(('Location', reverse('category:category_list')), response._headers['location'])

    def test_confirm_saved_object(self):
        from category.models import Category

        form_data = {'name': 'Foo'}
        self.post(form_data)
        category = Category.objects.get(pk=1)

        self.assertEqual(1, Category.active.count())
        self.assertEqual('Foo', category.name)
        self.assertEqual('foo', category.slug)

    def test_show_alert_message_after_save(self):
        form_data = {'name': 'Foo'}
        request, response = self.post(form_data)

        self.assert_redirect(response, reverse('category:category_list'))
        message = 'Category %s was created successfully!' % form_data['name']
        self.assert_message_exists(request, messages.SUCCESS, message)

    def test_html_content_with_a_unbound_form(self):
        response = self.get()

        self.assertNotContains(response, 'INVALID VARIABLE:')
        self.assertContains(response, 'Add A Category', count=2)
        self.assertContains(response, 'id="id_name"')
        self.assertContains(response, reverse('category:category_list'))

    def test_view_redirect_if_anonymous(self):
        request = self.factory.get(path=self.url, user=self.anonymous_user)
        response = self.view(request)

        self.assertEqual(302, response.status_code)
        self.assertEqual('%s?next=%s' % (reverse('login'), self.url), response._headers['location'][1])

    def get(self):
        request = self.factory.get(path=self.url, user=self.mock_user)
        response = self.view(request)
        return response.render()

    def post(self, form_data):
        request = self.factory.post(path=self.url, data=form_data, user=self.mock_user)
        return request, self.view(request)


class CategoryEditViewTest(BaseTestCase):
    from category.views import CategoryUpdateView

    view_class = CategoryUpdateView
    middleware_classes = [
        SessionMiddleware,
        (MessageMiddleware, MiddlewareType.PROCESS_REQUEST),
    ]

    def test_has_form_on_context(self):
        from category.forms import CategoryForm

        category = mommy.make('Category')
        response = self.get(category)

        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(response, 'category/edit.html')
        self.assertIsInstance(response.context_data['form'], CategoryForm)

    def test_should_show_form_with_errors(self):
        category = mommy.make('Category')
        _, response = self.post(category, {})
        form = response.context_data['form']

        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(response, 'category/edit.html')
        self.assertEqual(1, len(form.errors))
        self.assertTrue(form['name'].errors)

    def test_redirect_after_save(self):
        category = mommy.make('Category')
        form_data = {'name': 'foo'}
        _, response = self.post(category, form_data)

        self.assertEqual(302, response.status_code)
        self.assertEqual(('Location', reverse('category:category_list')), response._headers['location'])

    def test_confirm_saved_object(self):
        from category.models import Category

        old_category = mommy.make('Category', name='Foo')
        form_data = {'name': 'Bar'}
        self.post(old_category, form_data)
        new_category = self.refresh(old_category)

        self.assertEqual(1, Category.objects.count())
        self.assertEqual('Bar', new_category.name)
        self.assertEqual(old_category.slug, new_category.slug)

    def test_show_alert_message_after_save(self):
        old_category = mommy.make('Category', name='Foo')
        form_data = {'name': 'Bar'}
        self.post(old_category, form_data)
        new_category = self.refresh(old_category)
        request, response = self.post(old_category, form_data)

        self.assert_redirect(response, reverse('category:category_list'))
        message = 'Category %s was updated successfully!' % new_category.name
        self.assert_message_exists(request, messages.SUCCESS, message)

    def test_html_content_with_a_bound_form(self):
        category = mommy.make('Category')
        response = self.get(category)

        self.assertNotContains(response, 'INVALID VARIABLE:')
        self.assertContains(response, 'Edit Category', count=2)
        self.assertContains(response, category.name)
        self.assertContains(response, reverse('category:category_delete', kwargs={'slug': category.slug}))

    def test_view_redirect_if_anonymous(self):
        slug = 'foo'
        url = reverse('category:category_edit', kwargs={'slug': slug})
        request = self.factory.get(path=url, user=self.anonymous_user)
        response = self.view(request, slug=slug)

        self.assertEqual(302, response.status_code)
        self.assertEqual('%s?next=%s' % (reverse('login'), url), response._headers['location'][1])

    def get(self, category):
        url = reverse('category:category_edit', kwargs={'slug': category.slug})
        request = self.factory.get(path=url, user=self.mock_user)
        response = self.view(request, slug=category.slug)
        return response.render()

    def post(self, category, form_data):
        url = reverse('category:category_edit', kwargs={'slug': category.slug})
        request = self.factory.post(path=url, data=form_data, user=self.mock_user)
        return request, self.view(request, slug=category.slug)


class CategoryDeleteViewTest(BaseTestCase):
    from category.views import CategoryDeleteView

    view_class = CategoryDeleteView

    def test_view_response(self):
        category = mommy.make('Category')
        response = self.get(category)

        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(response, 'category/delete.html')
        self.assertEqual(category, response.context_data['category'])

    def test_view_redirect_after_delete(self):
        category = mommy.make('Category',)
        response = self.post(category)

        self.assertEqual(302, response.status_code)
        self.assertEqual(reverse('category:category_list'), response._headers['location'][1])

    def test_confirm_deleted_object(self):
        from category.models import Category

        old_category = mommy.make('Category',)
        self.post(old_category)
        new_category = self.refresh(old_category)

        self.assertEqual(1, Category.objects.count())
        self.assertEqual(0, Category.active.count())
        self.assertTrue(new_category.is_deleted)

    def test_html_content_on_delete_view(self):
        category = mommy.make('Category')
        response = self.get(category)

        self.assertNotContains(response, 'INVALID VARIABLE:')
        self.assertContains(response, 'Delete Category', count=2)
        self.assertContains(response, 'Are you sure you want to delete "%s"?' % category.name)
        self.assertContains(response, reverse('category:category_list'))

    def test_view_redirect_if_anonymous(self):
        slug = 'foo'
        url = reverse('category:category_delete', kwargs={'slug': slug})
        request = self.factory.get(path=url, user=self.anonymous_user)
        response = self.view(request, slug=slug)

        self.assertEqual(302, response.status_code)
        self.assertEqual('%s?next=%s' % (reverse('login'), url), response._headers['location'][1])

    def get(self, category):
        url = reverse('category:category_delete', kwargs={'slug': category.slug})
        request = self.factory.get(path=url, user=self.mock_user)
        response = self.view(request, slug=category.slug)
        return response.render()

    def post(self, category):
        url = reverse('category:category_delete', kwargs={'slug': category.slug})
        request = self.factory.post(path=url, user=self.mock_user)
        return self.view(request, slug=category.slug)
