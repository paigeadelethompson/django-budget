from __future__ import unicode_literals

from django.contrib import messages
from django.contrib.messages.middleware import MessageMiddleware
from django.contrib.sessions.middleware import SessionMiddleware
from django.core.paginator import Page, Paginator
from django.core.urlresolvers import reverse

from djet.testcases import MiddlewareType
from model_mommy import mommy
from rebar.testing import flatten_to_dict

from base.utils import BaseTestCase


class TransactionListViewTest(BaseTestCase):
    from transaction.views import TransactionListView

    url = reverse('transaction:transaction_list')
    view_class = TransactionListView

    def test_view_with_no_transaction(self):
        response = self.get()

        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(response, 'transaction/list.html')
        self.assertContains(response, reverse('transaction:transaction_add'))
        self.assertIsInstance(response.context_data['paginator'], Paginator)
        self.assertIsInstance(response.context_data['page_obj'], Page)
        self.assertFalse(response.context_data['is_paginated'])
        self.assertEqual(0, response.context_data['transactions'].count())

    def test_view_with_no_active_transaction(self):
        mommy.make('Transaction', is_deleted=True)
        response = self.get()

        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(response, 'transaction/list.html')
        self.assertContains(response, reverse('transaction:transaction_add'))
        self.assertIsInstance(response.context_data['paginator'], Paginator)
        self.assertIsInstance(response.context_data['page_obj'], Page)
        self.assertFalse(response.context_data['is_paginated'])
        self.assertEqual(0, response.context_data['transactions'].count())

    def test_view_with_a_transaction(self):
        transaction = mommy.make('Transaction')
        response = self.get()

        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(response, 'transaction/list.html')
        self.assertIsInstance(response.context_data['paginator'], Paginator)
        self.assertIsInstance(response.context_data['page_obj'], Page)
        self.assertFalse(response.context_data['is_paginated'])
        self.assertEqual(1, response.context_data['transactions'].count())
        self.assertIn(transaction, response.context_data['transactions'])

    def test_view_pagination(self):
        mommy.make('Transaction', _quantity=10)
        transaction = mommy.make('Transaction')

        url = '%s?page=2' % self.url
        request = self.factory.get(path=url, user=self.mock_user)
        response = self.view(request)
        response.render()

        self.assertIsInstance(response.context_data['paginator'], Paginator)
        self.assertIsInstance(response.context_data['page_obj'], Page)
        self.assertTrue(response.context_data['is_paginated'])
        self.assertEqual(1, response.context_data['transactions'].count())
        self.assertIn(transaction, response.context_data['transactions'])

    def test_html_content_with_no_transaction(self):
        response = self.get()

        self.assertNotContains(response, 'INVALID VARIABLE:')
        self.assertContains(response, 'Transaction List', count=2)
        self.assertContains(response, 'New Transaction')
        self.assertContains(response, reverse('transaction:transaction_add'))
        self.assertContains(response, 'No transactions found.')

    def test_html_content_with_a_transaction(self):
        category = mommy.make('Category')
        transaction = mommy.make('Transaction', notes='foo', category=category)
        response = self.get()

        self.assertNotContains(response, 'INVALID VARIABLE:')
        self.assertContains(response, 'Transaction List', count=2)
        self.assertContains(response, reverse('transaction:transaction_add'))
        self.assertNotContains(response, 'No transactions found.')
        self.assertContains(response, transaction.id)
        self.assertContains(response, transaction.notes)
        self.assertContains(response, transaction.get_transaction_type_display())
        self.assertContains(response, transaction.date.strftime('%m/%d/%Y'))
        self.assertContains(response, transaction.category.name)
        self.assertContains(response, transaction.amount)
        self.assertContains(response, reverse('transaction:transaction_edit', kwargs={'pk': transaction.id}))
        self.assertContains(response, reverse('transaction:transaction_delete', kwargs={'pk': transaction.id}))

    def test_view_redirect_if_anonymous(self):
        request = self.factory.get(path=self.url, user=self.anonymous_user)
        response = self.view(request)

        self.assertEqual(302, response.status_code)
        self.assertEqual('%s?next=%s' % (reverse('login'), self.url), response._headers['location'][1])

    def get(self):
        request = self.factory.get(path=self.url, user=self.mock_user)
        response = self.view(request)
        return response.render()


class TransactionAddViewTest(BaseTestCase):
    from transaction.views import TransactionCreateView

    url = url = reverse('transaction:transaction_add')
    view_class = TransactionCreateView
    middleware_classes = [
        SessionMiddleware,
        (MessageMiddleware, MiddlewareType.PROCESS_REQUEST),
    ]

    def test_has_form_on_context(self):
        from transaction.forms import TransactionForm

        response = self.get()

        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(response, 'transaction/add.html')
        self.assertIsInstance(response.context_data['form'], TransactionForm)

    def test_show_form_with_errors(self):
        form_data = {}
        _, response = self.post(form_data)
        response.render()
        form = response.context_data['form']

        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(response, 'transaction/add.html')
        self.assertEqual(4, len(form.errors))
        self.assertTrue(form['transaction_type'].errors)
        self.assertTrue(form['category'].errors)
        self.assertTrue(form['amount'].errors)
        self.assertTrue(form['date'].errors)

    def test_redirects_after_save(self):
        from transaction.forms import TransactionForm

        category = mommy.make('Category')
        transaction = mommy.prepare('Transaction', category=category)
        form_data = flatten_to_dict(TransactionForm(instance=transaction))
        _, response = self.post(form_data)

        self.assertEqual(302, response.status_code)
        self.assertEqual(('Location', reverse('transaction:transaction_list')), response._headers['location'])

    def test_confirm_saved_object(self):
        from transaction.models import Transaction
        from transaction.forms import TransactionForm

        category = mommy.make('Category')
        old = mommy.prepare('Transaction', category=category)
        form_data = flatten_to_dict(TransactionForm(instance=old))
        self.post(form_data)
        new = Transaction.objects.get(pk=1)

        self.assertEqual(1, Transaction.objects.count())
        self.assertEqual(old.transaction_type, new.transaction_type)
        self.assertEqual(old.category, new.category)
        self.assertEqual(old.amount, new.amount)
        self.assertEqual(old.notes, new.notes)
        self.assertEqual(old.date, new.date)

    def test_show_aleter_message_after_save(self):
        from transaction.forms import TransactionForm

        category = mommy.make('Category')
        old = mommy.prepare('Transaction', category=category)
        form_data = flatten_to_dict(TransactionForm(instance=old))
        request, response = self.post(form_data)

        self.assert_redirect(response, reverse('transaction:transaction_list'))
        message = 'Transaction was created successfuly!'
        self.assert_message_exists(request, messages.SUCCESS, message)

    def test_html_with_a_unbound_form(self):
        response = self.get()

        self.assertNotContains(response, 'INVALID VARIABLE:')
        self.assertContains(response, 'Add A Transaction', count=2)
        self.assertContains(response, 'id="id_notes"')
        self.assertContains(response, 'id="id_category"')
        self.assertContains(response, 'id="id_amount"')
        self.assertContains(response, 'id="id_date"')
        self.assertContains(response, reverse('transaction:transaction_list'))

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


class TransactionEditViewTest(BaseTestCase):
    from transaction.views import TransactionUpdateView

    view_class = TransactionUpdateView
    middleware_classes = [
        SessionMiddleware,
        (MessageMiddleware, MiddlewareType.PROCESS_REQUEST),
    ]

    def test_has_form_on_context(self):
        from transaction.forms import TransactionForm

        transaction = mommy.make('Transaction')
        response = self.get(transaction)

        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(response, 'transaction/edit.html')
        self.assertIsInstance(response.context_data['form'], TransactionForm)

    def test_empy_post_should_show_form_with_errors(self):
        transaction = mommy.make('Transaction')
        form_data = {}
        _, response = self.post(transaction, form_data)
        response.render()
        form = response.context_data['form']

        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(response, 'transaction/add.html')
        self.assertEqual(4, len(form.errors))
        self.assertTrue(form['transaction_type'].errors)
        self.assertTrue(form['category'].errors)
        self.assertTrue(form['amount'].errors)
        self.assertTrue(form['date'].errors)
        self.assertFalse(form['notes'].errors)

    def test_redirects_after_save(self):
        from transaction.forms import TransactionForm

        transaction = mommy.make('Transaction')
        form_data = flatten_to_dict(TransactionForm(instance=transaction))
        _, response = self.post(transaction, form_data)

        self.assertEqual(302, response.status_code)
        self.assertEqual(reverse('transaction:transaction_list'), response._headers['location'][1])

    def test_confirm_saved_object(self):
        from transaction.models import Transaction
        from transaction.forms import TransactionForm

        old = mommy.make('Transaction', notes='Foo')
        form_data = flatten_to_dict(TransactionForm(instance=old))
        form_data['notes'] = 'Bar'
        self.post(old, form_data)
        new = Transaction.active.get(pk=1)

        self.assertEqual(1, Transaction.active.count())
        self.assertEqual(old.transaction_type, new.transaction_type)
        self.assertEqual('Bar', new.notes)
        self.assertEqual(old.category, new.category)
        self.assertEqual(old.amount, new.amount)
        self.assertEqual(old.date, new.date)

    def test_show_alert_message_after_save(self):
        from transaction.forms import TransactionForm

        old = mommy.make('Transaction')
        form_data = flatten_to_dict(TransactionForm(instance=old))
        request, response = self.post(old, form_data)

        self.assert_redirect(response, reverse('transaction:transaction_list'))
        message = 'Transaction was updated successfuly!'
        self.assert_message_exists(request, messages.SUCCESS, message)

    def test_view_html_with_a_bound_from(self):
        transaction = mommy.make('Transaction')
        response = self.get(transaction)

        self.assertNotContains(response, 'INVALID VARIABLE:')
        self.assertContains(response, 'Edit Transaction', count=2)
        self.assertContains(response, transaction.transaction_type)
        self.assertContains(response, transaction.get_transaction_type_display())
        self.assertContains(response, transaction.notes)
        self.assertContains(response, transaction.category.name)
        self.assertContains(response, transaction.date)
        self.assertContains(response, reverse('transaction:transaction_list'))
        self.assertContains(response, reverse('transaction:transaction_delete', kwargs={'pk': transaction.pk}))

    def test_view_redirect_if_anonymous(self):
        pk = 1
        url = reverse('transaction:transaction_edit', kwargs={'pk': pk})
        request = self.factory.get(path=url, user=self.anonymous_user)
        response = self.view(request, pk=pk)

        self.assertEqual(302, response.status_code)
        self.assertEqual('%s?next=%s' % (reverse('login'), url), response._headers['location'][1])

    def get(self, transaction):
        url = reverse('transaction:transaction_edit', kwargs={'pk': transaction.id})
        request = self.factory.get(path=url, user=self.mock_user)
        response = self.view(request, pk=transaction.id)
        return response.render()

    def post(self, transaction, form_data):
        url = reverse('transaction:transaction_edit', kwargs={'pk': transaction.id})
        request = self.factory.post(path=url, data=form_data, user=self.mock_user)
        return request, self.view(request, pk=transaction.id)


class TransactionDeleteViewTest(BaseTestCase):
    from transaction.views import TransactionDeleteView

    view_class = TransactionDeleteView

    def test_view_status_code_and_template_on_get(self):
        transaction = mommy.make('Transaction')
        response = self.get(transaction)

        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(response, 'transaction/delete.html')

    def test_view_redirects_after_delete(self):
        transaction = mommy.make('Transaction')
        response = self.post(transaction)

        self.assertEqual(302, response.status_code)
        self.assertEqual(('Location', reverse('transaction:transaction_list')), response._headers['location'])

    def test_confirm_deleted_object(self):
        from transaction.models import Transaction

        old_transaction = mommy.make('Transaction')
        self.post(old_transaction)
        new_transaction = self.refresh(old_transaction)

        self.assertEqual(1, Transaction.objects.count())
        self.assertEqual(0, Transaction.active.count())
        self.assertTrue(new_transaction.is_deleted)

    def test_html_content_on_delete_view(self):
        transaction = mommy.make('Transaction')
        response = self.get(transaction)

        self.assertNotContains(response, 'INVALID VARIABLE:')
        self.assertContains(response, 'Delete Transaction', count=2)
        self.assertContains(response, 'Are you sure you want to delete "%s"?' % transaction)
        self.assertContains(response, reverse('transaction:transaction_list'))

    def test_view_redirect_if_anonymous(self):
        pk = 1
        url = reverse('transaction:transaction_delete', kwargs={'pk': pk})
        request = self.factory.get(path=url, user=self.anonymous_user)
        response = self.view(request, pk=pk)

        self.assertEqual(302, response.status_code)
        self.assertEqual('%s?next=%s' % (reverse('login'), url), response._headers['location'][1])

    def get(self, transaction):
        url = reverse('transaction:transaction_delete', kwargs={'pk': transaction.id})
        request = self.factory.get(path=url, user=self.mock_user)
        response = self.view(request, pk=transaction.id)
        return response.render()

    def post(self, transaction):
        url = reverse('transaction:transaction_delete', kwargs={'pk': transaction.id})
        request = self.factory.post(path=url, user=self.mock_user)
        response = self.view(request, pk=transaction.id)
        return response
