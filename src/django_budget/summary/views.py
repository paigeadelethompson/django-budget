from __future__ import unicode_literals

from calendar import monthrange
from datetime import date

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.views.generic.dates import ArchiveIndexView

from braces.views import LoginRequiredMixin

from django_budget.budget.models import Budget
from django_budget.transaction.models import Transaction


class SummaryArchiveView(LoginRequiredMixin, ArchiveIndexView):
    model = Transaction
    template_name = "summary/list.html"
    date_field = 'date'
    date_list_period = 'month'
    queryset = Transaction.active.all()
    allow_empty = True


summary_list = SummaryArchiveView.as_view()


@login_required
def summary_year(request, year):
    start_date = date(int(year), 1, 1)
    end_date = date(int(year), 12, 31)

    try:
        budget = Budget.active.most_current_for_date(end_date)
        estimates_and_transactions, actual_total = budget.estimates_and_transactions(start_date, end_date)

    except Budget.DoesNotExist:
        budget = None
        estimates_and_transactions = None
        actual_total = None

    context = {'start_date': start_date,
               'budget': budget,
               'actual_total': actual_total,
               'estimates_and_transactions': estimates_and_transactions}

    return render(request, 'summary/year.html', context)


@login_required
def summary_month(request, year, month):
    start_date = date(int(year), int(month), 1)
    _, last_day_of_month = monthrange(int(year), int(month))
    end_date = date(int(year), int(month), last_day_of_month)

    try:
        budget = Budget.active.most_current_for_date(end_date)
        estimates_and_transactions, actual_total = budget.estimates_and_transactions(start_date, end_date)

    except Budget.DoesNotExist:
        budget = None
        estimates_and_transactions = None
        actual_total = None

    context = {'start_date': start_date,
               'estimates_and_transactions': estimates_and_transactions,
               'actual_total': actual_total,
               'budget': budget}

    return render(request, 'summary/month.html', context)
