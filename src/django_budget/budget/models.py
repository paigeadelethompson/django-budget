from __future__ import unicode_literals

from datetime import date
from decimal import Decimal

from django.db import models
from django.db.models import Sum
from django.utils.translation import gettext_lazy as _
from six import python_2_unicode_compatible

from django_budget.base.models import ActiveManager, StandardMetadata
from django_budget.category.models import Category
from django_budget.transaction.models import Transaction


class BudgetLatestManager(ActiveManager):
    def most_current_for_date(self, date):
        return super(BudgetLatestManager, self).get_query_set().filter(start_date__lte=date).latest('start_date')


@python_2_unicode_compatible
class Budget(StandardMetadata):
    name = models.CharField(_('Name'), max_length=100)
    slug = models.SlugField(_('Slug'), unique=True)
    start_date = models.DateField(_('Start Date'),
                                  default=date.today,
                                  db_index=True)

    objects = models.Manager()
    active = BudgetLatestManager()

    def __str__(self):
        return self.name

    def actual_total(self, start_date, end_date):
        actual_total = Decimal('0.0')

        for estimate in self.estimates.exclude(is_deleted=True):
            actual_amount = estimate.actual_amount(start_date, end_date)
            actual_total += actual_amount

        return actual_total

    def estimates_and_transactions(self, start_date, end_date):
        estimates_and_transactions = []
        actual_total = Decimal('0.0')

        for estimate in self.estimates.exclude(is_deleted=True):
            actual_amount = estimate.actual_amount(start_date, end_date)
            actual_total += actual_amount
            estimates_and_transactions.append({
                'estimate': estimate,
                'transactions': estimate.actual_transactions(start_date, end_date),
                'actual_amount': actual_amount,
            })

        return (estimates_and_transactions, actual_total)

    def monthly_estimated_total(self):
        total = Decimal('0.0')
        for estimate in self.estimates.exclude(is_deleted=True):
            total += estimate.amount
        return total

    def yearly_estimated_total(self):
        return self.monthly_estimated_total() * 12

    class Meta:
        verbose_name = _('Budget')
        verbose_name_plural = _('Budgets')


@python_2_unicode_compatible
class BudgetEstimate(StandardMetadata):
    budget = models.ForeignKey(Budget,
                               related_name='estimates',
                               verbose_name=_('Budget'),
                               limit_choices_to={'is_deleted': False}, on_delete=models.DO_NOTHING)
    category = models.ForeignKey(Category,
                                 related_name='estimates',
                                 verbose_name=_('Category'),
                                 limit_choices_to={'is_deleted': False}, on_delete=models.DO_NOTHING)
    amount = models.DecimalField(_('Amount'), max_digits=11, decimal_places=2)

    objects = models.Manager()
    active = ActiveManager()

    def __str__(self):
        return '%s - %.02f' % (self.category.name, self.amount)

    def actual_transactions(self, start_date, end_date):
        return Transaction.expenses.filter(category=self.category,
                                           date__range=(start_date, end_date)
                                           ).order_by('date')

    def actual_amount(self, start_date, end_date):
        return Transaction.expenses.filter(category=self.category,
                                           date__range=(start_date, end_date)
                                           ).aggregate(Sum('amount'))['amount__sum'] or Decimal('0.0')

    def yearly_estimated_amount(self):
        return self.amount * 12

    class Meta:
        verbose_name = _('Budget estimate')
        verbose_name_plural = _('Budget estimates')
