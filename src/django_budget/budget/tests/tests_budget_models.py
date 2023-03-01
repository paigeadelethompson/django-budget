from __future__ import unicode_literals

from datetime import date, timedelta
from decimal import Decimal

from django.test import TestCase

from model_mommy import mommy


class BudgetModelTest(TestCase):

    def test_create_new_budget(self):
        budget = mommy.make('Budget')

        self.assertTrue(budget.name)
        self.assertTrue(budget.slug)
        self.assertTrue(budget.start_date)
        self.assertFalse(budget.is_deleted)

    def test_budget_unicode_string(self):
        budget = mommy.make('Budget')
        self.assertTrue(budget.name, str(budget))

    def test_budget_active_manager(self):
        from budget.models import Budget

        mommy.make(Budget, is_deleted=True)

        self.assertEqual(1, Budget.objects.count())
        self.assertEqual(0, Budget.active.count())

    def test_budget_actual_total(self):
        budget = mommy.make('Budget')
        category = mommy.make('Category')
        start_date, end_date = date.today(), date.today()
        mommy.make('Transaction', amount=Decimal('10.0'), date=start_date, category=category)
        mommy.make('Transaction', amount=Decimal('10.0'), date=start_date, category=category)
        mommy.make('BudgetEstimate', category=category, budget=budget)

        self.assertEqual(Decimal('20.0'), budget.actual_total(start_date, end_date))

    def test_budget_actual_total_with_deleted_transaction(self):
        start_date, end_date = date.today(), date.today()
        budget = mommy.make('Budget')
        category = mommy.make('Category')
        mommy.make('Transaction', is_deleted=True, date=start_date, category=category)
        mommy.make('BudgetEstimate', category=category, budget=budget)

        self.assertEqual(0, budget.actual_total(start_date, end_date))

    def test_budget_estimates_and_transactions(self):
        budget = mommy.make('Budget')
        start_date, end_date = date.today(), date.today()

        c1 = mommy.make('Category')
        t1 = mommy.make('Transaction', amount=Decimal('25.0'), date=start_date, category=c1)
        t2 = mommy.make('Transaction', amount=Decimal('75.0'), date=start_date, category=c1)
        e1 = mommy.make('BudgetEstimate', category=c1, budget=budget)

        c2 = mommy.make('Category')
        t3 = mommy.make('Transaction', amount=Decimal('30.0'), date=start_date, category=c2)
        e2 = mommy.make('BudgetEstimate', category=c2, budget=budget)

        estimates, total = budget.estimates_and_transactions(start_date, end_date)

        self.assertEqual(Decimal('130.0'), total)
        self.assertEqual(2, len(estimates))

        self.assertIn(t1, estimates[0]['transactions'])
        self.assertIn(t2, estimates[0]['transactions'])
        self.assertEqual(e1, estimates[0]['estimate'])
        self.assertEqual(Decimal('100.0'), estimates[0]['actual_amount'])

        self.assertIn(t3, estimates[1]['transactions'])
        self.assertEqual(e2, estimates[1]['estimate'])
        self.assertEqual(Decimal('30.0'), estimates[1]['actual_amount'])

    def test_budget_most_current_for_date(self):
        from budget.models import Budget

        today = date.today()
        yesterday = today - timedelta(days=1)
        tomorrow = today + timedelta(days=1)
        end_date = today + timedelta(days=7)

        mommy.make(Budget, start_date=yesterday)
        mommy.make(Budget, start_date=today)
        budget = mommy.make(Budget, start_date=tomorrow)

        self.assertEqual(3, Budget.active.count())
        self.assertEqual(budget, Budget.active.most_current_for_date(end_date))
