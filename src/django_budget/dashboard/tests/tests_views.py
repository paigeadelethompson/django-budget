from __future__ import unicode_literals

from decimal import Decimal

from django.core.urlresolvers import reverse

from model_mommy import mommy

from base.utils import BaseTestCase


class DashboardViewTest(BaseTestCase):
    from dashboard.views import dashboard

    view_function = dashboard

    def test_view_redirects_if_no_budgets(self):
        url = reverse('dashboard')
        request = self.factory.get(path=url, user=self.mock_user)
        response = self.view(request)

        self.assertEqual(302, response.status_code)
        self.assertEqual(('Location', reverse('setup')), response._headers['location'])

    def test_view_with_no_transactions(self):
        budget = mommy.make('Budget')
        response = self.get()

        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(response, 'dashboard.html')
        self.assertEqual(budget, response.context['budget'])
        self.assertEqual(0, response.context['latest_expenses'].count())
        self.assertEqual(0, response.context['latest_incomes'].count())
        self.assertEqual(Decimal('0.0'), response.context['estimated_amount'])
        self.assertEqual(Decimal('0.0'), response.context['amount_used'])
        self.assertEqual(0, response.context['progress_bar_percent'])

    def test_view_with_budget_not_bound_with_transaction(self):
        from transaction.models import Transaction

        budget = mommy.make('Budget')
        expense = mommy.make('Transaction')
        income = mommy.make('Transaction', transaction_type=Transaction.INCOME)
        response = self.get()

        self.assertEqual(200, response.status_code)
        self.assertEqual(budget, response.context['budget'])
        self.assertEqual(1, response.context['latest_expenses'].count())
        self.assertIn(expense, response.context['latest_expenses'])
        self.assertEqual(1, response.context['latest_incomes'].count())
        self.assertIn(income, response.context['latest_incomes'])
        self.assertEqual(Decimal('0.0'), response.context['estimated_amount'])
        self.assertEqual(Decimal('0.0'), response.context['amount_used'])
        self.assertEqual(0, response.context['progress_bar_percent'])

    def test_view_with_budget_bound_with_transactions(self):
        from transaction.models import Transaction

        budget = mommy.make('Budget')
        category = mommy.make('Category')
        mommy.make('BudgetEstimate', budget=budget, category=category, amount=Decimal('10.0'))
        expense1 = mommy.make('Transaction', category=category, amount=Decimal('2.5'))
        expense2 = mommy.make('Transaction', category=category, amount=Decimal('2.5'))
        income = mommy.make('Transaction', transaction_type=Transaction.INCOME)
        response = self.get()

        self.assertEqual(200, response.status_code)
        self.assertEqual(budget, response.context['budget'])
        self.assertEqual(2, response.context['latest_expenses'].count())
        self.assertIn(expense1, response.context['latest_expenses'])
        self.assertIn(expense2, response.context['latest_expenses'])
        self.assertEqual(1, response.context['latest_incomes'].count())
        self.assertIn(income, response.context['latest_incomes'])
        self.assertEqual(Decimal('5.0'), response.context['amount_used'])
        self.assertEqual(Decimal('10.0'), response.context['estimated_amount'])
        self.assertEqual(50, response.context['progress_bar_percent'])

    def test_view_with_progress_bar_percent_at_100(self):
        budget = mommy.make('Budget')
        category = mommy.make('Category')
        mommy.make('BudgetEstimate', budget=budget, category=category, amount=Decimal('1.0'))
        expense = mommy.make('Transaction', category=category, amount=Decimal('1.0'))
        response = self.get()

        self.assertEqual(200, response.status_code)
        self.assertEqual(budget, response.context['budget'])
        self.assertEqual(1, response.context['latest_expenses'].count())
        self.assertIn(expense, response.context['latest_expenses'])
        self.assertEqual([], list(response.context['latest_incomes']))
        self.assertEqual(Decimal('1.0'), response.context['amount_used'])
        self.assertEqual(Decimal('1.0'), response.context['estimated_amount'])
        self.assertEqual(100, response.context['progress_bar_percent'])

    def test_html_content_with_no_transactions(self):
        mommy.make('Budget')
        request = self.factory.get(user=self.mock_user)
        response = self.view(request)

        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(response, 'dashboard.html')
        self.assertContains(response, 'Dashboard', count=3)
        self.assertContains(response, 'No recent expenses found.')
        self.assertContains(response, 'No recent incomes found.')
        self.assertContains(response, 'style="width: 0%;"')
        self.assertContains(response, reverse('transaction:transaction_add'))

    def test_html_contetn_with_a_transactions(self):
        from transaction.models import Transaction

        budget = mommy.make('Budget')
        category = mommy.make('Category')
        mommy.make('BudgetEstimate', budget=budget, category=category, amount=Decimal('10.0'))
        expense = mommy.make(Transaction, category=category, amount=Decimal('7.5'))
        income = mommy.make(Transaction, category=category, transaction_type=Transaction.INCOME)
        response = self.getf()

        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(response, 'dashboard.html')
        self.assertNotContains(response, 'No recent expenses found.')
        self.assertNotContains(response, 'No recent incomes found.')
        self.assertContains(response, reverse('transaction:transaction_add'))

        self.assertContains(response, reverse('transaction:transaction_edit', kwargs={'pk': expense.id}))
        self.assertContains(response, expense.notes)
        self.assertContains(response, expense.date.strftime('%m/%d/%Y'))

        self.assertContains(response, reverse('transaction:transaction_edit', kwargs={'pk': income.id}))
        self.assertContains(response, income.notes)
        self.assertContains(response, income.date.strftime('%m/%d/%Y'))

        self.assertContains(response, 'style="width: 75%;"')

    def test_view_redirect_if_anonymous(self):
        url = reverse('dashboard')
        request = self.factory.get(path=url, user=self.anonymous_user)
        response = self.view(request)

        self.assertEqual(302, response.status_code)
        self.assertEqual('%s?next=%s' % (reverse('login'), url), response._headers['location'][1])

    def get(self):
        self.login()
        url = reverse('dashboard')
        return self.client.get(url)

    def getf(self):
        url = reverse('dashboard')
        request = self.factory.get(path=url, user=self.mock_user)
        return self.view(request)
