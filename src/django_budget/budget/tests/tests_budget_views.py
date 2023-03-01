from __future__ import unicode_literals

from datetime import date

from django.contrib import messages
from django.contrib.messages.middleware import MessageMiddleware
from django.contrib.sessions.middleware import SessionMiddleware
from django.core.paginator import Page, Paginator
from django.core.urlresolvers import reverse

from djet.testcases import MiddlewareType
from model_mommy import mommy

from base.utils import BaseTestCase


class BudgetViewListTest(BaseTestCase):
    from budget.views import BudgetListView

    view_class = BudgetListView
    url = reverse('budget:budget_list')

    def test_view_with_no_budgets(self):
        response = self.get()

        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(response, 'budget/list.html')
        self.assertIsInstance(response.context_data['paginator'], Paginator)
        self.assertIsInstance(response.context_data['page_obj'], Page)
        self.assertFalse(response.context_data['is_paginated'])
        self.assertEqual(0, response.context_data['budgets'].count())

    def test_view_with_a_budget(self):
        budget = mommy.make('Budget')
        response = self.get()

        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(response, 'budget/list.html')
        self.assertIsInstance(response.context_data['paginator'], Paginator)
        self.assertIsInstance(response.context_data['page_obj'], Page)
        self.assertFalse(response.context_data['is_paginated'])
        self.assertEqual(1, response.context_data['budgets'].count())
        self.assertIn(budget, response.context_data['budgets'])

    def test_view_with_no_active_budgets(self):
        mommy.make('Budget', is_deleted=True)
        response = self.get()

        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(response, 'budget/list.html')
        self.assertIsInstance(response.context_data['paginator'], Paginator)
        self.assertIsInstance(response.context_data['page_obj'], Page)
        self.assertFalse(response.context_data['is_paginated'])
        self.assertEqual(0, response.context_data['budgets'].count())

    def test_view_pagination(self):
        mommy.make('Budget', _quantity=10)
        budget = mommy.make('Budget')
        url = '%s?page=2' % self.url
        request = self.factory.get(path=url, user=self.mock_user)
        response = self.view(request)
        response.render()

        self.assertIsInstance(response.context_data['paginator'], Paginator)
        self.assertIsInstance(response.context_data['page_obj'], Page)
        self.assertTrue(response.context_data['is_paginated'])
        self.assertEqual(1, response.context_data['budgets'].count())
        self.assertIn(budget, response.context_data['budgets'])

    def test_html_content_with_no_budgets(self):
        response = self.get()

        self.assertNotContains(response, 'INVALID VARIABLE:')
        self.assertContains(response, 'Budget List', count=2)
        self.assertContains(response, 'New Budget')
        self.assertContains(response, reverse('budget:budget_add'))
        self.assertContains(response, 'No budgets found.')

    def test_html_content_with_a_budget(self):
        budget = mommy.make('Budget')
        response = self.get()

        self.assertNotContains(response, 'INVALID VARIABLE:')
        self.assertContains(response, 'Budget List', count=2)
        self.assertContains(response, 'New Budget')
        self.assertContains(response, reverse('budget:budget_add'))
        self.assertNotContains(response, 'No budgets found.')
        self.assertContains(response, budget.id)
        self.assertContains(response, budget.name)
        self.assertContains(response, reverse('budget:budget_edit', kwargs={'slug': budget.slug}))
        self.assertContains(response, reverse('budget:budget_delete', kwargs={'slug': budget.slug}))
        self.assertContains(response, reverse('budget:estimate_list', kwargs={'slug': budget.slug}))

    def test_redirect_if_anonymous(self):
        request = self.factory.get(path=self.url, user=self.anonymous_user)
        response = self.view(request)

        self.assertEqual(302, response.status_code)
        self.assertEqual('%s?next=%s' % (reverse('login'), self.url), response._headers['location'][1])

    def get(self):
        request = self.factory.get(path=self.url, user=self.mock_user)
        response = self.view(request)
        return response.render()


class BudgetAddViewTest(BaseTestCase):
    from budget.views import BudgetCreateView

    view_class = BudgetCreateView
    url = reverse('budget:budget_add')
    middleware_classes = [
        SessionMiddleware,
        (MessageMiddleware, MiddlewareType.PROCESS_REQUEST),
    ]

    def test_view_has_form_on_context(self):
        from budget.forms import BudgetForm

        response = self.get()

        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(response, 'budget/add.html')
        self.assertIsInstance(response.context_data['form'], BudgetForm)

    def test_view_show_form_with_errors(self):
        form_data = {}
        _, response = self.post(form_data)
        response.render()
        form = response.context_data['form']

        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(response, 'budget/add.html')
        self.assertEqual(2, len(form.errors))
        self.assertTrue(form['name'].errors)
        self.assertTrue(form['start_date'].errors)

    def test_redirects_after_save(self):
        form_data = {'name': 'foo', 'start_date': date.today()}
        _, response = self.post(form_data)

        self.assertEqual(302, response.status_code)
        self.assertEqual(('Location', reverse('budget:budget_list')), response._headers['location'])

    def test_confirm_saved_object(self):
        from budget.models import Budget

        form_data = {'name': 'foo', 'start_date': date.today()}
        self.post(form_data)
        new = Budget.objects.get(pk=1)

        self.assertEqual(1, Budget.objects.count())
        self.assertEqual('foo', new.name)
        self.assertEqual(date.today(), new.start_date)

    def test_show_alert_message_after_save(self):
        from budget.models import Budget

        form_data = {'name': 'foo', 'start_date': date.today()}
        request, response = self.post(form_data)
        budget = Budget.objects.get(pk=1)

        self.assert_redirect(response, reverse('budget:budget_list'))
        message = 'Budget %s was created successfuly!' % budget.name
        self.assert_message_exists(request, messages.SUCCESS, message)

    def test_html_with_a_unboun_form(self):
        response = self.get()

        self.assertContains(response, 'Add A Budget', count=2)
        self.assertContains(response, 'id="id_name"')
        self.assertContains(response, 'id="id_start_date"')
        self.assertContains(response, reverse('budget:budget_list'))

    def test_redirect_if_anonymous(self):
        url = reverse('budget:budget_add')
        request = self.factory.get(path=url, user=self.anonymous_user)
        response = self.view(request)

        self.assertEqual(302, response.status_code)
        self.assertEqual('%s?next=%s' % (reverse('login'), url), response._headers['location'][1])

    def get(self):
        request = self.factory.get(path=self.url, user=self.mock_user)
        response = self.view(request)
        return response.render()

    def post(self, form_data):
        request = self.factory.post(paht=self.url, data=form_data, user=self.mock_user)
        response = self.view(request)
        return request, response


class BudgetEditViewTest(BaseTestCase):
    from budget.views import BudgetUpdateView

    view_class = BudgetUpdateView
    middleware_classes = [
        SessionMiddleware,
        (MessageMiddleware, MiddlewareType.PROCESS_REQUEST),
    ]

    def test_has_form_on_context(self):
        from budget.forms import BudgetForm

        budget = mommy.make('Budget')
        response = self.get(budget)

        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(response, 'budget/edit.html')
        self.assertIsInstance(response.context_data['form'], BudgetForm)

    def test_show_form_with_errors(self):
        budget = mommy.make('Budget')
        form_data = {}
        _, response = self.post(budget, form_data)
        form = response.context_data['form']

        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(response, 'budget/edit.html')
        self.assertEqual(2, len(form.errors))
        self.assertTrue(form['name'].errors)
        self.assertTrue(form['start_date'].errors)

    def test_redirects_after_save(self):
        budget = mommy.make('Budget')
        form_data = {'name': 'foo', 'start_date': budget.start_date}
        _, response = self.post(budget, form_data)

        self.assertEqual(302, response.status_code)
        self.assertEqual(('Location', reverse('budget:budget_list')), response._headers['location'])

    def test_confirm_saved_object(self):
        from budget.models import Budget

        old = mommy.make('Budget', name='Foo')
        form_data = {'name': 'Bar', 'start_date': old.start_date}
        self.post(old, form_data)
        new = self.refresh(old)

        self.assertEqual(1, Budget.objects.count())
        self.assertEqual('Bar', new.name)
        self.assertEqual(old.start_date, new.start_date)

    def test_show_alert_message_after_save(self):

        old = mommy.make('Budget', name='Foo')
        form_data = {'name': 'Bar', 'start_date': old.start_date}
        request, response = self.post(old, form_data)
        new = self.refresh(old)

        self.assert_redirect(response, reverse('budget:budget_list'))
        message = 'Budget %s was updated successfuly!' % new.name
        self.assert_message_exists(request, messages.SUCCESS, message)

    def test_html_content_with_a_bound_form(self):
        budget = mommy.make('Budget')
        response = self.get(budget)

        self.assertNotContains(response, 'INVALID VARIABLE:')
        self.assertContains(response, 'Edit Budget', count=2)
        self.assertContains(response, budget.name)
        self.assertContains(response, budget.start_date.strftime('%Y-%m-%d'))
        self.assertContains(response, reverse('budget:budget_list'))
        self.assertContains(response, reverse('budget:budget_delete', kwargs={'slug': budget.slug}))

    def test_redirect_if_anonymous(self):
        slug = 'foo'
        url = reverse('budget:budget_edit', kwargs={'slug': slug})
        request = self.factory.get(path=url, user=self.anonymous_user)
        response = self.view(request, slug=slug)

        self.assertEqual(302, response.status_code)
        self.assertEqual('%s?next=%s' % (reverse('login'), url), response._headers['location'][1])

    def get(self, budget):
        url = reverse('budget:budget_edit', kwargs={'slug': budget.slug})
        request = self.factory.get(path=url, user=self.mock_user)
        response = self.view(request, slug=budget.slug)
        return response.render()

    def post(self, budget, form_data):
        url = reverse('budget:budget_edit', kwargs={'slug': budget.slug})
        request = self.factory.post(path=url, data=form_data, user=self.mock_user)
        response = self.view(request, slug=budget.slug)
        return request, response


class BudgetDeleteViewTest(BaseTestCase):
    from budget.views import BudgetDeleteView

    view_class = BudgetDeleteView

    def test_view_response_code_and_template_on_get(self):
        budget = mommy.make('Budget')
        response = self.get(budget)

        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(response, 'budget/delete.html')

    def test_view_redirect_after_delete(self):
        budget = mommy.make('Budget')
        response = self.post(budget)

        self.assertEqual(302, response.status_code)
        self.assertEqual(('Location', reverse('budget:budget_list')), response._headers['location'])

    def test_confirm_deleted_object(self):
        from budget.models import Budget

        old = mommy.make('Budget')
        self.post(old)
        new = Budget.objects.get(pk=1)

        self.assertEqual(1, Budget.objects.count())
        self.assertEqual(0, Budget.active.count())
        self.assertTrue(new.is_deleted)

    def test_html_content_on_delete_view(self):
        budget = mommy.make('Budget')
        response = self.get(budget)

        self.assertNotContains(response, 'INVALID VARIABLE:')
        self.assertContains(response, 'Delete Budget', count=2)
        self.assertContains(response, 'Are you sure you want to delete "%s"?' % budget.name)
        self.assertContains(response, reverse('budget:budget_list'))

    def test_redirect_if_anonymous(self):
        slug = 'foo'
        url = reverse('budget:budget_delete', kwargs={'slug': slug})
        request = self.factory.get(path=url, user=self.anonymous_user)
        response = self.view(request, slug=slug)

        self.assertEqual(302, response.status_code)
        self.assertEqual('%s?next=%s' % (reverse('login'), url), response._headers['location'][1])

    def get(self, budget):
        url = reverse('budget:budget_delete', kwargs={'slug': budget.slug})
        request = self.factory.get(path=url, user=self.mock_user)
        response = self.view(request, slug=budget.slug)
        return response.render()

    def post(self, budget):
        url = reverse('budget:budget_delete', kwargs={'slug': budget.slug})
        request = self.factory.post(path=url, user=self.mock_user)
        return self.view(request, slug=budget.slug)
