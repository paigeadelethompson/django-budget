from __future__ import unicode_literals

from datetime import date, timedelta
from decimal import Decimal

from django.core.urlresolvers import reverse
from model_mommy import mommy

from base.utils import BaseTestCase


class SummaryArchiveViewTest(BaseTestCase):
    from summary.views import SummaryArchiveView

    view_class = SummaryArchiveView

    def test_view_with_no_transaction(self):
        response = self.get()

        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(response, 'summary/list.html')
        self.assertEqual([], list(response.context_data['date_list']))

    def test_view_with_a_transaction(self):
        transaction = mommy.make('Transaction')
        response = self.get()
        month = transaction.date.replace(day=1)

        self.assertEqual(1, response.context_data['date_list'].count())
        self.assertIn(month, response.context_data['date_list'])

    def test_view_with_no_active_transaction(self):
        from transaction.models import Transaction

        mommy.make('Transaction', is_deleted=True)
        response = self.get()

        self.assertEqual(1, Transaction.objects.count())
        self.assertEqual([], list(response.context_data['date_list']))

    def test_view_with_two_transactions_in_different_months(self):
        t1 = mommy.make('Transaction')
        t2 = mommy.make('Transaction', date=t1.date - timedelta(days=35))
        month_1 = t1.date.replace(day=1)
        month_2 = t2.date.replace(day=1)
        request = self.factory.get(user=self.mock_user)
        response = self.view(request)

        self.assertEqual(2, response.context_data['date_list'].count())
        self.assertIn(month_1, response.context_data['date_list'])
        self.assertIn(month_2, response.context_data['date_list'])

    def test_html_content_with_no_transaction(self):
        response = self.get()

        self.assertContains(response, 'Summaries', count=3)
        self.assertContains(response, "It looks like there haven't been any transactions, so there's nothing to show here.")

    def test_html_content_with_two_transactions_in_different_years(self):
        t1 = mommy.make('Transaction')
        t2 = mommy.make('Transaction', date=t1.date - timedelta(days=360))
        response = self.get()

        self.assertNotContains(response, "It looks like there haven't been any transactions, so there's nothing to show here.")
        self.assertContains(response, t1.date.year)
        self.assertContains(response, t1.date.strftime('%B'))
        self.assertContains(response, reverse('summary:summary_year', kwargs={'year': t1.date.year}))
        self.assertContains(response, reverse('summary:summary_month', kwargs={'year': t1.date.year, 'month': t1.date.month}))

        self.assertContains(response, t2.date.year)
        self.assertContains(response, t2.date.strftime('%B'))
        self.assertContains(response, reverse('summary:summary_year', kwargs={'year': t2.date.year}))
        self.assertContains(response, reverse('summary:summary_month', kwargs={'year': t2.date.year, 'month': t2.date.month}))

    def test_redirect_if_anonymous(self):
        url = reverse('summary:summary_list')
        request = self.factory.get(path=url, user=self.anonymous_user)
        response = self.view(request)

        self.assertEqual(302, response.status_code)
        self.assertEqual('%s?next=%s' % (reverse('login'), url), response._headers['location'][1])

    def get(self):
        url = reverse('summary:summary_list')
        request = self.factory.get(path=url, user=self.mock_user)
        return self.view(request)


class SummaryYearViewTest(BaseTestCase):
    from summary.views import summary_year

    view_function = summary_year

    def test_view_with_no_budget(self):
        start_date = date.today().replace(day=1).replace(month=1)

        response = self.get(start_date.year)

        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(response, 'summary/year.html')
        self.assertEqual(None, response.context['budget'])
        self.assertEqual(start_date, response.context['start_date'])
        self.assertEqual(None, response.context['actual_total'])
        self.assertEqual(None, response.context['estimates_and_transactions'])

    def test_view_with_no_estimate_and_no_transaction(self):
        budget = mommy.make('Budget')
        start_date = date(budget.start_date.year, 1, 1)
        response = self.get(budget.start_date.year)

        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(response, 'summary/year.html')
        self.assertEqual(budget, response.context['budget'])
        self.assertEqual(start_date, response.context['start_date'])
        self.assertEqual(Decimal('0.0'), response.context['actual_total'])
        self.assertEqual([], response.context['estimates_and_transactions'])

    def test_view_with_two_estimates_and_no_transaction(self):

        budget = mommy.make('Budget')
        e1 = mommy.make('BudgetEstimate', budget=budget)
        e2 = mommy.make('BudgetEstimate', budget=budget)
        response = self.get(budget.start_date.year)

        self.assertEqual(Decimal('0.0'), response.context['actual_total'])
        self.assertEqual(2, len(response.context['estimates_and_transactions']))
        self.assertEqual(e1, response.context['estimates_and_transactions'][0]['estimate'])
        self.assertEqual([], list(response.context['estimates_and_transactions'][0]['transactions']))
        self.assertEqual(Decimal('0.0'), response.context['estimates_and_transactions'][0]['actual_amount'])
        self.assertEqual(e2, response.context['estimates_and_transactions'][1]['estimate'])
        self.assertEqual(Decimal('0.0'), response.context['estimates_and_transactions'][1]['actual_amount'])
        self.assertEqual([], list(response.context['estimates_and_transactions'][1]['transactions']))

    def test_view_with_estimates_and_transactions(self):
        budget = mommy.make('Budget')
        c1 = mommy.make('Category')
        e1 = mommy.make('BudgetEstimate', budget=budget, category=c1)
        t1 = mommy.make('Transaction', category=c1)

        c2 = mommy.make('Category')
        e2 = mommy.make('BudgetEstimate', budget=budget, category=c2)
        t2 = mommy.make('Transaction', category=c2)
        actual_total = t1.amount + t2.amount

        response = self.get(budget.start_date.year)

        self.assertEqual(200, response.status_code)
        self.assertEqual(actual_total, response.context['actual_total'])
        self.assertEqual(2, len(response.context['estimates_and_transactions']))

        self.assertEqual(e1, response.context['estimates_and_transactions'][0]['estimate'])
        self.assertIn(t1, response.context['estimates_and_transactions'][0]['transactions'])
        self.assertEqual(t1.amount, response.context['estimates_and_transactions'][0]['actual_amount'])

        self.assertEqual(e2, response.context['estimates_and_transactions'][1]['estimate'])
        self.assertEqual(t2.amount, response.context['estimates_and_transactions'][1]['actual_amount'])
        self.assertIn(t2, response.context['estimates_and_transactions'][1]['transactions'])

    def test_html_content_with_no_estimate_and_no_transaction(self):
        budget = mommy.make('Budget')
        year = budget.start_date.year
        response = self.get(year)

        self.assertEqual(200, response.status_code)
        self.assertContains(response, 'Summary Year For %s' % year, count=2)
        self.assertContains(response, budget.name)
        self.assertContains(response, 'No data to show.')

    def test_html_content_with_estimates_and_transactions(self):
        budget = mommy.make('Budget')
        start_date = date(budget.start_date.year, 1, 1)
        category = mommy.make('Category')
        estimate = mommy.make('BudgetEstimate', budget=budget, category=category)
        t1 = mommy.make('Transaction', category=category, notes='Notes 1')
        t2 = mommy.make('Transaction', category=category, notes='Notes 2')

        url = reverse('summary:summary_year', kwargs={'year': budget.start_date.year})
        request = self.factory.get(path=url, user=self.mock_user)
        response = self.view(request, year=start_date.year)

        self.assertEqual(200, response.status_code)
        self.assertContains(response, 'Summary Year For %s' % start_date.year, count=2)
        self.assertContains(response, budget.name)
        self.assertNotContains(response, 'No data to show.')
        self.assertNotContains(response, "Not found no budget this year!")
        self.assertContains(response, category.name)
        self.assertContains(response, t1.notes)
        self.assertContains(response, t1.date.strftime('%m/%d/%Y'))
        self.assertContains(response, t2.notes)
        self.assertContains(response, t2.date.strftime('%m/%d/%Y'))
        self.assertContains(response, estimate.yearly_estimated_amount())
        self.assertContains(response, budget.yearly_estimated_total())

    def test_html_content_with_no_budget(self):
        year = 2014
        response = self.getf(year)

        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(response, 'summary/year.html')
        self.assertContains(response, "Not found no budget this year!")

    def test_redirect_if_anonymous(self):
        year = 2014
        url = reverse('summary:summary_year', kwargs={'year': year})
        request = self.factory.get(path=url, user=self.anonymous_user)
        response = self.view(request, year=year)

        self.assertEqual(302, response.status_code)
        self.assertEqual('%s?next=%s' % (reverse('login'), url), response._headers['location'][1])

    def get(self, year):
        self.login()
        url = reverse('summary:summary_year', kwargs={'year': year})
        return self.client.get(url)

    def getf(self, year):
        url = reverse('summary:summary_year', kwargs={'year': year})
        request = self.factory.get(path=url, user=self.mock_user)
        return self.view(request, year=year)


class SummaryMonthViewTest(BaseTestCase):
    from summary.views import summary_month

    view_function = summary_month

    def test_view_with_no_budget(self):
        start_date = date.today().replace(day=1).replace(month=1)

        response = self.get(start_date.year, start_date.month)

        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(response, 'summary/month.html')
        self.assertEqual(None, response.context['budget'])
        self.assertEqual(start_date, response.context['start_date'])
        self.assertEqual(None, response.context['actual_total'])
        self.assertEqual(None, response.context['estimates_and_transactions'])

    def test_view_with_no_estimate_and_no_transaction(self):
        budget = mommy.make('Budget')
        start_date = date(budget.start_date.year, budget.start_date.month, 1)
        response = self.get(budget.start_date.year, budget.start_date.month)

        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(response, 'summary/month.html')
        self.assertEqual(budget, response.context['budget'])
        self.assertEqual(start_date, response.context['start_date'])
        self.assertEqual(Decimal('0.0'), response.context['actual_total'])
        self.assertEqual([], response.context['estimates_and_transactions'])

    def test_view_with_estimates_and_transactions(self):
        budget = mommy.make('Budget')
        category = mommy.make('Category')
        estimate = mommy.make('BudgetEstimate', budget=budget, category=category)
        t1 = mommy.make('Transaction', category=category, notes='Notes 1')
        t2 = mommy.make('Transaction', category=category, notes='Notes 2')
        start_date = date(budget.start_date.year, budget.start_date.month, 1)
        response = self.get(budget.start_date.year, budget.start_date.month)

        self.assertEqual(200, response.status_code)
        self.assertEqual(budget, response.context['budget'])
        self.assertEqual(start_date, response.context['start_date'])
        self.assertEqual(t1.amount + t2.amount, response.context['actual_total'])
        self.assertEqual(1, len(response.context['estimates_and_transactions']))
        self.assertEqual(estimate, response.context['estimates_and_transactions'][0]['estimate'])
        self.assertIn(t1, response.context['estimates_and_transactions'][0]['transactions'])
        self.assertIn(t2, response.context['estimates_and_transactions'][0]['transactions'])

    def test_html_content_with_no_estimates_and_no_transaction(self):
        budget = mommy.make('Budget')
        start_date = date(budget.start_date.year, budget.start_date.month, 1)
        response = self.get(budget.start_date.year, budget.start_date.month)

        self.assertEqual(200, response.status_code)
        self.assertContains(response, 'Month Summary For %s' % start_date.strftime('%B %Y'), count=2)
        self.assertContains(response, budget.name)
        self.assertContains(response, 'No data to show.')

    def test_html_content_with_estimates_and_transaction(self):
        budget = mommy.make('Budget')
        category = mommy.make('Category')
        estimate = mommy.make('BudgetEstimate', budget=budget, category=category)
        transaction = mommy.make('Transaction', category=category, notes='Notes 1')
        year = budget.start_date.year
        month = budget.start_date.month
        start_date = date(year, month, 1)
        response = self.getf(year, month)

        self.assertEqual(200, response.status_code)
        self.assertContains(response, 'Month Summary For %s' % start_date.strftime('%B %Y'), count=2)
        self.assertContains(response, budget.name)
        self.assertNotContains(response, 'No data to show.')
        self.assertNotContains(response, 'Not found no budget this month!')
        self.assertContains(response, category.name)
        self.assertContains(response, transaction.notes)
        self.assertContains(response, transaction.amount)
        self.assertContains(response, transaction.date.strftime('%m/%d/%Y'))
        self.assertContains(response, estimate.amount)
        self.assertContains(response, budget.monthly_estimated_total())

    def test_html_content_with_no_budget(self):
        response = self.getf(2014, 2)

        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(response, 'summary/month.html')
        self.assertContains(response, 'Not found no budget this month!')

    def test_redirect_if_anonymous(self):
        year = 2014
        month = 1
        url = reverse('summary:summary_month', kwargs={'year': year, 'month': month})
        request = self.factory.get(path=url, user=self.anonymous_user)
        response = self.view(request, year=year, month=month)

        self.assertEqual(302, response.status_code)
        self.assertEqual('%s?next=%s' % (reverse('login'), url), response._headers['location'][1])

    def get(self, year, month):
        url = reverse('summary:summary_month', kwargs={'year': year, 'month': month})
        self.login()
        return self.client.get(url)

    def getf(self, year, month):
        url = reverse('summary:summary_month', kwargs={'year': year, 'month': month})
        request = self.factory.get(path=url, user=self.mock_user)
        response = self.view(request, year=year, month=month)
        return response
