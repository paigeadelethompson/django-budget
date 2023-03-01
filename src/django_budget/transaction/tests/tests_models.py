from __future__ import unicode_literals

from datetime import timedelta
from decimal import Decimal

from django.test import TestCase
from django.core.exceptions import ValidationError

from model_mommy import mommy


class TransactionModelTest(TestCase):

    def test_create_new_transaction(self):
        from transaction.models import Transaction

        transaction = mommy.make('Transaction')

        self.assertFalse(transaction.notes)
        self.assertTrue(transaction.amount)
        self.assertTrue(transaction.date)
        self.assertEqual(Transaction.EXPENSE, transaction.transaction_type)
        self.assertFalse(transaction.is_deleted)

    def test_create_new_transaction_with_income_transaction_type(self):
        from transaction.models import Transaction

        transaction = mommy.make(Transaction, transaction_type=Transaction.INCOME)

        self.assertEqual(Transaction.INCOME, transaction.transaction_type)

    def test_create_new_transaction_whith_invalid_transaction_type(self):
        from transaction.models import Transaction

        transaction = mommy.make(Transaction, transaction_type=3)

        self.assertRaises(ValidationError, transaction.full_clean)

    def test_transaction_unicode_string(self):
        from transaction.models import Transaction

        t = mommy.make(Transaction, notes='Foo', amount=Decimal('1.0'))

        self.assertEqual(u'Foo (Expense) - 1.00', str(t))

    def test_active_transaction_manager(self):
        from transaction.models import Transaction

        mommy.make('Transaction', is_deleted=True)

        self.assertEqual(1, Transaction.objects.count())
        self.assertEqual(0, Transaction.active.count())

    def test_latest_transaction_manager(self):
        from transaction.models import Transaction

        mommy.make('Transaction', _quantity=11)

        self.assertEqual(11, Transaction.objects.count())
        self.assertEqual(10, Transaction.latest.get_latest().count())

    def test_income_transaction_manager(self):
        from transaction.models import Transaction

        mommy.make(Transaction)
        self.assertEqual(0, Transaction.incomes.count())

        mommy.make(Transaction, transaction_type=Transaction.INCOME)
        self.assertEqual(1, Transaction.incomes.count())

    def test_expense_transaction_manager(self):
        from transaction.models import Transaction

        mommy.make(Transaction, transaction_type=Transaction.INCOME)
        self.assertEqual(0, Transaction.expenses.count())

        mommy.make(Transaction, _quantity=2)
        self.assertEqual(2, Transaction.expenses.count())

    def test_confirm_deleted_object(self):
        transaction = mommy.make('Transaction')
        transaction.delete()

        self.assertTrue(transaction.is_deleted)

    def test_months_transaction_manager(self):
        from transaction.models import Transaction

        t1 = mommy.make('Transaction')
        t2 = mommy.make('Transaction', date=t1.date - timedelta(days=35))
        month_1 = t1.date.replace(day=1)
        month_2 = t2.date.replace(day=1)

        self.assertEqual(2, Transaction.months.count())
        self.assertIn(month_1, Transaction.months.all())
        self.assertIn(month_2, Transaction.months.all())
