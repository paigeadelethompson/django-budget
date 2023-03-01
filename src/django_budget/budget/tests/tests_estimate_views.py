from __future__ import unicode_literals

from decimal import Decimal

from django.contrib import messages
from django.contrib.messages.middleware import MessageMiddleware
from django.contrib.sessions.middleware import SessionMiddleware
from django.core.paginator import Page, Paginator
from django.core.urlresolvers import reverse

from djet.testcases import MiddlewareType
from model_mommy import mommy
from rebar.testing import flatten_to_dict

from base.utils import BaseTestCase


class BudgetEstimateListViewTest(BaseTestCase):
    from budget.views import BudgetEstimateListView

    view_class = BudgetEstimateListView

    def test_view_with_no_estimates(self):
        budget = mommy.make('Budget')
        response = self.get(budget)

        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(response, 'estimate/list.html')
        self.assertEqual([], list(response.context_data['estimates']))
        self.assertEqual(budget, response.context_data['budget'])
        self.assertIsInstance(response.context_data['paginator'], Paginator)
        self.assertIsInstance(response.context_data['page_obj'], Page)
        self.assertFalse(response.context_data['is_paginated'])

    def test_view_with_a_estimate(self):
        budget = mommy.make('Budget')
        estimate = mommy.make('BudgetEstimate', budget=budget)
        response = self.get(budget)

        self.assertIsInstance(response.context_data['paginator'], Paginator)
        self.assertIsInstance(response.context_data['page_obj'], Page)
        self.assertFalse(response.context_data['is_paginated'])
        self.assertEqual(1, response.context_data['estimates'].count())
        self.assertIn(estimate, response.context_data['estimates'])

    def test_view_with_no_active_estimates(self):
        budget = mommy.make('Budget')
        mommy.make('BudgetEstimate', budget=budget, is_deleted=True)
        response = self.get(budget)

        self.assertIsInstance(response.context_data['paginator'], Paginator)
        self.assertIsInstance(response.context_data['page_obj'], Page)
        self.assertFalse(response.context_data['is_paginated'])
        self.assertEqual(0, response.context_data['estimates'].count())

    def test_view_pagination(self):
        budget = mommy.make('Budget')
        mommy.make('BudgetEstimate', budget=budget, _quantity=10)
        estimate = mommy.make('BudgetEstimate', budget=budget)
        url = '%s?page=2' % reverse('budget:estimate_list', kwargs={'slug': budget.slug})
        request = self.factory.get(path=url, user=self.mock_user)
        response = self.view(request, slug=budget.slug)
        response.render()

        self.assertIsInstance(response.context_data['paginator'], Paginator)
        self.assertIsInstance(response.context_data['page_obj'], Page)
        self.assertTrue(response.context_data['is_paginated'])
        self.assertEqual(1, response.context_data['estimates'].count())
        self.assertIn(estimate, response.context_data['estimates'])

    def test_html_content_with_no_estimate(self):
        budget = mommy.make('Budget')
        response = self.get(budget)

        self.assertNotContains(response, 'INVALID VARIABLE:')
        self.assertContains(response, 'Estimate List For %s' % budget.name)
        self.assertContains(response, reverse('budget:budget_edit', kwargs={'slug': budget.slug}))
        self.assertContains(response, 'No estimates found.')

    def test_html_content_with_a_estimate(self):
        budget = mommy.make('Budget')
        estimate = mommy.make('BudgetEstimate', budget=budget)
        response = self.get(estimate.budget)

        self.assertNotContains(response, 'INVALID VARIABLE:')
        self.assertContains(response, 'Estimate List For %s' % budget.name)
        self.assertContains(response, reverse('budget:budget_edit', kwargs={'slug': budget.slug}))
        self.assertNotContains(response, 'No estimates found.')
        self.assertContains(response, reverse('budget:estimate_add', kwargs={'slug': budget.slug}))
        self.assertContains(response, estimate.id)
        self.assertContains(response, reverse('budget:estimate_edit', kwargs={'slug': budget.slug, 'pk': estimate.id}))
        self.assertContains(response, estimate.category.name)
        self.assertContains(response, reverse('budget:estimate_delete', kwargs={'slug': budget.slug, 'pk': estimate.id}))

    def test_redirect_if_anonymous(self):
        slug = 'foo'
        url = reverse('budget:estimate_list', kwargs={'slug': slug})
        request = self.factory.get(path=url, user=self.anonymous_user)
        response = self.view(request, slug=slug)

        self.assertEqual(302, response.status_code)
        self.assertEqual('%s?next=%s' % (reverse('login'), url), response._headers['location'][1])

    def get(self, budget):
        url = reverse('budget:estimate_list', kwargs={'slug': budget.slug})
        request = self.factory.get(path=url, user=self.mock_user)
        response = self.view(request, slug=budget.slug)
        return response.render()


class EstimateCreateViewTest(BaseTestCase):
    from budget.views import BudgetEstimateCreateView

    view_class = BudgetEstimateCreateView
    middleware_classes = [
        SessionMiddleware,
        (MessageMiddleware, MiddlewareType.PROCESS_REQUEST),
    ]

    def test_has_form_on_context(self):
        from budget.forms import BudgetEstimateForm

        budget = mommy.make('Budget')
        response = self.get(budget)

        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(response, 'estimate/add.html')
        self.assertIsInstance(response.context_data['form'], BudgetEstimateForm)

    def test_show_form_with_errors(self):
        budget = mommy.make('Budget')
        _, response = self.post(budget, {})
        form = response.context_data['form']

        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(response, 'estimate/add.html')
        self.assertEqual(2, len(form.errors))
        self.assertTrue(form['category'].errors)
        self.assertTrue(form['amount'].errors)

    def test_redirects_after_save(self):
        from budget.forms import BudgetEstimateForm

        budget = mommy.make('Budget')
        category = mommy.make('Category')
        estimate = mommy.prepare('BudgetEstimate', category=category, budget=budget)
        form_data = flatten_to_dict(BudgetEstimateForm(instance=estimate))
        _, response = self.post(estimate.budget, form_data)

        self.assertEqual(302, response.status_code)
        self.assertEqual(('Location', reverse('budget:budget_list')), response._headers['location'])

    def test_confirm_saved_object(self):
        from budget.models import BudgetEstimate

        budget = mommy.make('Budget')
        category = mommy.make('Category')
        form_data = {'category': category.id, 'amount': Decimal('1.0')}
        self.post(budget, form_data)
        estimate = BudgetEstimate.objects.get(pk=1)

        self.assertEqual(1, BudgetEstimate.objects.count())
        self.assertEqual(budget, estimate.budget)
        self.assertEqual(category, estimate.category)
        self.assertEqual(Decimal('1.0'), estimate.amount)

    def test_show_alert_message_after_save(self):
        budget = mommy.make('Budget')
        category = mommy.make('Category')
        form_data = {'category': category.id, 'amount': Decimal('1.0')}
        request, response = self.post(budget, form_data)

        self.assert_redirect(response, reverse('budget:budget_list'))
        message = 'Estimate was created successfuly!'
        self.assert_message_exists(request, messages.SUCCESS, message)

    def test_html_content_with_a_unbound(self):
        budget = mommy.make('Budget')
        response = self.get(budget)

        self.assertNotContains(response, 'INVALID VARIABLE:')
        self.assertContains(response, 'Add An Estimate', count=2)
        self.assertContains(response, 'id="id_category"')
        self.assertContains(response, 'id="id_amount"')
        self.assertContains(response, reverse('budget:budget_list'))

    def test_redirect_if_anonymous(self):
        slug = 'foo'
        url = reverse('budget:estimate_add', kwargs={'slug': slug})
        request = self.factory.get(path=url, user=self.anonymous_user)
        response = self.view(request, slug=slug)

        self.assertEqual(302, response.status_code)
        self.assertEqual('%s?next=%s' % (reverse('login'), url), response._headers['location'][1])

    def get(self, budget):
        url = reverse('budget:estimate_add', kwargs={'slug': budget.slug})
        request = self.factory.get(path=url, user=self.mock_user)
        response = self.view(request, slug=budget.slug)
        return response.render()

    def post(self, budget, form_data):
        url = reverse('budget:estimate_add', kwargs={'slug': budget.slug})
        request = self.factory.post(path=url, data=form_data, user=self.mock_user)
        response = self.view(request, slug=budget.slug)
        return request, response


class BudgetEstimateUpdateViewTest(BaseTestCase):
    from budget.views import BudgetEstimateUpdateView

    view_class = BudgetEstimateUpdateView
    middleware_classes = [
        SessionMiddleware,
        (MessageMiddleware, MiddlewareType.PROCESS_REQUEST),
    ]

    def test_view_context(self):
        from budget.forms import BudgetEstimateForm

        budget = mommy.make('Budget')
        estimate = mommy.make('BudgetEstimate', budget=budget)
        response = self.get(estimate)

        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(response, 'estimate/edit.html')
        self.assertIsInstance(response.context_data['form'], BudgetEstimateForm)
        self.assertEqual(estimate, response.context_data['estimate'])

    def test_show_form_with_errors(self):
        budget = mommy.make('Budget')
        estimate = mommy.make('BudgetEstimate', budget=budget)
        _, response = self.post(estimate, {})
        form = response.context_data['form']

        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(response, 'estimate/edit.html')
        self.assertEqual(2, len(form.errors))
        self.assertTrue(form['amount'].errors)
        self.assertTrue(form['category'].errors)

    def test_redirects_after_save(self):
        budget = mommy.make('Budget')
        estimate = mommy.make('BudgetEstimate', budget=budget)
        form_data = {'amount': estimate.amount,
                     'category': estimate.category.id}
        _, response = self.post(estimate, form_data)

        self.assertEqual(302, response.status_code)
        self.assertEqual(('Location', reverse('budget:budget_list')), response._headers['location'])

    def test_confirm_saved_object(self):
        from budget.models import BudgetEstimate

        budget = mommy.make('Budget')
        old = mommy.make('BudgetEstimate', budget=budget)
        form_data = {'amount': Decimal('9.0'),
                     'category': old.category.id}
        self.post(old, form_data)
        new = self.refresh(old)

        self.assertEqual(1, BudgetEstimate.objects.count())
        self.assertEqual(Decimal('9.0'), new.amount)
        self.assertEqual(old.category, new.category)

    def test_show_alert_message_after_save(self):
        budget = mommy.make('Budget')
        old = mommy.make('BudgetEstimate', budget=budget)
        form_data = {'amount': Decimal('9.0'),
                     'category': old.category.id}
        request, response = self.post(old, form_data)

        self.assert_redirect(response, reverse('budget:budget_list'))
        message = 'Estimate was updated successfuly!'
        self.assert_message_exists(request, messages.SUCCESS, message)

    def test_html_content_with_a_bound_form(self):
        budget = mommy.make('Budget')
        estimate = mommy.make('BudgetEstimate', budget=budget)
        response = self.get(estimate)

        self.assertContains(response, 'Edit Estimate', count=2)
        self.assertContains(response, estimate.category)
        self.assertContains(response, reverse('budget:estimate_delete', kwargs={'slug': budget.slug, 'pk': estimate.pk}))
        self.assertContains(response, reverse('budget:budget_list'))

    def test_redirect_if_anonymous(self):
        slug = 'foo'
        pk = 1
        url = reverse('budget:estimate_edit', kwargs={'slug': slug, 'pk': pk})
        request = self.factory.get(path=url, user=self.anonymous_user)
        response = self.view(request, slug=slug, pk=pk)

        self.assertEqual(302, response.status_code)
        self.assertEqual('%s?next=%s' % (reverse('login'), url), response._headers['location'][1])

    def get(self, estimate):
        url = reverse('budget:estimate_edit', kwargs={'slug': estimate.budget.slug, 'pk': estimate.pk})
        request = self.factory.get(path=url, user=self.mock_user)
        response = self.view(request, slug=estimate.budget.slug, pk=estimate.pk)
        return response.render()

    def post(self, estimate, form_data):
        url = reverse('budget:estimate_edit', kwargs={'slug': estimate.budget.slug, 'pk': estimate.pk})
        request = self.factory.post(path=url, data=form_data, user=self.mock_user)
        response = self.view(request, slug=estimate.budget.slug, pk=estimate.pk)
        return request, response


class BudgetEstimateDeleteViewTest(BaseTestCase):
    from budget.views import BudgetEstimateDeleteView

    view_class = BudgetEstimateDeleteView

    def test_view_reponse(self):
        budget = mommy.make('Budget')
        estimate = mommy.make('BudgetEstimate', budget=budget)
        response = self.get(estimate)

        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(response, 'estimate/delete.html')

    def test_view_redirect_after_delete(self):
        budget = mommy.make('Budget')
        estimate = mommy.make('BudgetEstimate', budget=budget)
        response = self.post(estimate)

        self.assertEqual(302, response.status_code)
        self.assertEqual(('Location', reverse('budget:budget_list')), response._headers['location'])

    def test_confirm_deleted_object(self):
        from budget.models import BudgetEstimate

        budget = mommy.make('Budget')
        old = mommy.make('BudgetEstimate', budget=budget)
        self.post(old)
        new = BudgetEstimate.objects.get(pk=1)

        self.assertEqual(1, BudgetEstimate.objects.count())
        self.assertEqual(0, BudgetEstimate.active.count())
        self.assertTrue(new.is_deleted)

    def test_html_content_on_delete_view(self):
        budget = mommy.make('Budget')
        estimate = mommy.make('BudgetEstimate', budget=budget)
        response = self.get(estimate)

        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(response, 'estimate/delete.html')
        self.assertContains(response, 'Delete Estimate', count=2)
        self.assertContains(response, 'Are you sure you want to delete "%s"?' % estimate)
        self.assertContains(response, reverse('budget:budget_list'))

    def test_redirect_if_anonymous(self):
        slug = 'foo'
        pk = 1
        url = reverse('budget:estimate_edit', kwargs={'slug': slug, 'pk': pk})
        request = self.factory.get(path=url, user=self.anonymous_user)
        response = self.view(request, slug=slug, pk=pk)

        self.assertEqual(302, response.status_code)
        self.assertEqual('%s?next=%s' % (reverse('login'), url), response._headers['location'][1])

    def get(self, estimate):
        url = reverse('budget:estimate_delete', kwargs={'slug': estimate.budget.slug, 'pk': estimate.pk})
        request = self.factory.get(path=url, user=self.mock_user)
        response = self.view(request, slug=estimate.budget.slug, pk=estimate.pk)
        return response.render()

    def post(self, estimate):
        url = reverse('budget:estimate_delete', kwargs={'slug': estimate.budget.slug, 'pk': estimate.pk})
        request = self.factory.post(path=url, user=self.mock_user)
        return self.view(request, slug=estimate.budget.slug, pk=estimate.pk)
