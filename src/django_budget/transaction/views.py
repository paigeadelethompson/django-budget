from __future__ import unicode_literals

from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView
from django.utils.translation import gettext_lazy as _

from braces.views import LoginRequiredMixin

from .forms import TransactionForm
from .models import Transaction


class TransactionListView(LoginRequiredMixin, ListView):
    model = Transaction
    template_name = 'transaction/list.html'
    context_object_name = 'transactions'
    queryset = Transaction.active.all().select_related()
    paginate_by = 10


transaction_list = TransactionListView.as_view()


class TransactionCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Transaction
    form_class = TransactionForm
    template_name = 'transaction/add.html'
    success_url = reverse_lazy('transaction-list')
    success_message = _('Transaction was created successfuly!')


transaction_add = TransactionCreateView.as_view()


class TransactionUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Transaction
    template_name = 'transaction/edit.html'
    form_class = TransactionForm
    success_url = reverse_lazy('transaction-list')
    success_message = _('Transaction was updated successfully!')


transaction_edit = TransactionUpdateView.as_view()


class TransactionDeleteView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    model = Transaction
    template_name = 'transaction/delete.html'
    success_url = reverse_lazy('transaction-list')
    success_message = _('Transaction was deleted!')


transaction_delete = TransactionDeleteView.as_view()
