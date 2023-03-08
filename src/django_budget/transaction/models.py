from __future__ import unicode_literals

from datetime import date

from django.db import models
from django.utils.translation import gettext_lazy as _
from six import python_2_unicode_compatible
from django_budget.base.models import ActiveManager, StandardMetadata
from django_budget.category.models import Category


class TransactionLatestManager(ActiveManager):
    def get_latest(self, limit=10):
        return self.get_query_set().order_by('-date', '-created')[0:limit]


class TransactionIncomeManager(TransactionLatestManager):
    def get_query_set(self):
        return super(TransactionIncomeManager, self).get_query_set().filter(transaction_type=Transaction.INCOME)


class TransactionExpenseManager(TransactionLatestManager):
    def get_query_set(self):
        return super(TransactionExpenseManager, self).get_query_set().filter(transaction_type=Transaction.EXPENSE)


class TransactionByMonthManager(ActiveManager):
    def get_query_set(self):
        return super(TransactionByMonthManager, self).get_query_set().dates('date', 'month')


@python_2_unicode_compatible
class Transaction(StandardMetadata):
    EXPENSE = 'expense'
    INCOME = 'income'
    TRANSACTION_TYPES = (
        (INCOME, _('Income')),
        (EXPENSE, _('Expense')))

    transaction_type = models.CharField(_('Transaction Type'),
                                        choices=TRANSACTION_TYPES,
                                        max_length=32,
                                        default=EXPENSE,
                                        db_index=True)
    category = models.ForeignKey(Category,
                                 verbose_name=_('Category'),
                                 limit_choices_to={'is_deleted': False}, on_delete=models.DO_NOTHING)
    notes = models.TextField(_('Notes'), max_length=255, blank=True)
    amount = models.DecimalField(_('Amount'), max_digits=11, decimal_places=2)
    date = models.DateField(_('Date'), db_index=True, default=date.today)

    objects = models.Manager()
    active = ActiveManager()
    latest = TransactionLatestManager()
    incomes = TransactionIncomeManager()
    expenses = TransactionExpenseManager()
    months = TransactionByMonthManager()

    def __str__(self):
        return '%s (%s) - %.02f' % (self.notes,
                                    self.get_transaction_type_display(),
                                    self.amount)

    class Meta:
        verbose_name = _('Transaction')
        verbose_name_plural = _('Transactions')
