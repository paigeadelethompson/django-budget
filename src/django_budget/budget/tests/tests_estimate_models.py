from __future__ import unicode_literals

from datetime import date, timedelta
from decimal import Decimal

from django.test import TestCase

from model_mommy import mommy


class BudgetEstimateModel(TestCase):

    def teste_create_new_estimate(self):
        category = mommy.make('Category')
        budget = mommy.make('Budget')
        estimate = mommy.make('BudgetEstimate', category=category, budget=budget)

        self.assertTrue(estimate.amount)
        self.assertEqual(category, estimate.category)
        self.assertEqual(budget, estimate.budget)

    def test_estimate_unicode_string(self):
        estimate = mommy.make('BudgetEstimate', category__name='Foo', amount=Decimal('1.0'))

        self.assertEqual(u'Foo - 1.00', str(estimate))

    def test_estimate_active_manager(self):
        from budget.models import BudgetEstimate as Estimate

        mommy.make(Estimate, is_deleted=True)

        self.assertEqual(1, Estimate.objects.count())
        self.assertEqual(0, Estimate.active.count())

    def test_actual_transactions_with_two_transaction_in_date_range(self):
        category = mommy.make('Category')
        start_date, end_date = date.today(), date.today()
        t1 = mommy.make('Transaction', date=start_date, category=category)
        t2 = mommy.make('Transaction', date=start_date, category=category)
        estimate = mommy.make('BudgetEstimate', category=category)

        self.assertEqual(2, estimate.actual_transactions(start_date, end_date).count())
        self.assertIn(t1, list(estimate.actual_transactions(start_date, end_date)))
        self.assertIn(t2, list(estimate.actual_transactions(start_date, end_date)))

    def test_actual_transactions_with_transaction_outside_the_date_range(self):
        category = mommy.make('Category')
        start_date, end_date = date.today(), date.today()
        t = mommy.make('Transaction', date=start_date - timedelta(1), category=category)
        estimate = mommy.make('BudgetEstimate', category=category)

        self.assertEqual(0, estimate.actual_transactions(start_date, end_date).count())
        self.assertNotIn(t, list(estimate.actual_transactions(start_date, end_date)))

    def test_estimate_actual_transactions_with_income_transaction(self):
        from transaction.models import Transaction

        category = mommy.make('Category')
        t = mommy.make('Transaction', transaction_type=Transaction.INCOME, category=category)
        estimate = mommy.make('BudgetEstimate', category=category)
        start_date, end_date = t.date, t.date

        self.assertEqual(0, estimate.actual_transactions(start_date, end_date).count())
        self.assertNotIn(t, list(estimate.actual_transactions(start_date, end_date)))

    def test_estimate_actual_amount(self):
        category = mommy.make('Category')
        t = mommy.make('Transaction', amount=Decimal('3.0'), category=category)
        mommy.make('Transaction', amount=Decimal('7.0'), date=t.date, category=category)
        estimate = mommy.make('BudgetEstimate', category=category)

        self.assertEqual(Decimal('10.0'), estimate.actual_amount(t.date, t.date))

    def test_yearly_estimated_amount(self):
        estimate = mommy.make('BudgetEstimate', amount=Decimal('3.0'))

        self.assertEqual(Decimal('36.0'), estimate.yearly_estimated_amount())
