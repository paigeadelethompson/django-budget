from __future__ import unicode_literals

from datetime import date
from decimal import Decimal

from django.test import TestCase

from model_mommy import mommy


class TransactionFormTestCase(TestCase):

    def test_form_save(self):
        from transaction.forms import TransactionForm
        from transaction.models import Transaction

        category = mommy.make('Category')
        form_data = {'transaction_type': Transaction.EXPENSE,
                     'category': category.id,
                     'amount': Decimal('1.0'),
                     'date': date.today(),
                     'notes': ''}
        form = TransactionForm(data=form_data)

        self.assertTrue(form.is_valid())

    def test_deleted_category_should_not_to_show_in_form(self):
        from transaction.forms import TransactionForm

        category = mommy.make('Category', is_deleted=True)
        form = TransactionForm()

        self.assertNotIn((category.id, category.name), form.fields['category'].choices)
