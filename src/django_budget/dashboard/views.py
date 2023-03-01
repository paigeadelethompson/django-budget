from __future__ import unicode_literals

from datetime import date, timedelta
from decimal import InvalidOperation

from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils import timezone

from django_budget.budget.models import Budget
from django_budget.transaction.models import Transaction


@login_required
def dashboard(request):
    try:
        budget = Budget.active.most_current_for_date(timezone.now())

    except Budget.DoesNotExist:
        return redirect('setup')

    latest_expenses = Transaction.expenses.get_latest()
    latest_incomes = Transaction.incomes.get_latest()

    now = timezone.now()
    start_date = date(now.year, now.month, 1)
    end_year, end_month = now.year, now.month + 1

    end_date = date(end_year, end_month + 1, 1) - timedelta(days=1)

    estimated_amount = budget.monthly_estimated_total()
    amount_used = budget.actual_total(start_date, end_date)

    try:
        progress_bar_percent = min(100, amount_used / estimated_amount * 100)

    except InvalidOperation:
        progress_bar_percent = 0

    ctx = {'budget': budget,
           'estimated_amount': estimated_amount,
           'amount_used': amount_used,
           'latest_incomes': latest_incomes,
           'latest_expenses': latest_expenses,
           'progress_bar_percent': progress_bar_percent}

    return render(request, 'dashboard.html', ctx)
