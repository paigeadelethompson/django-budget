from __future__ import unicode_literals

from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404
from django.views.generic import CreateView, DeleteView, ListView, UpdateView
from django.utils.translation import gettext_lazy as _

from braces.views import LoginRequiredMixin

from .forms import BudgetEstimateForm, BudgetForm
from .models import Budget, BudgetEstimate


class BudgetListView(LoginRequiredMixin, ListView):
    model = Budget
    template_name = 'budget/list.html'
    context_object_name = 'budgets'
    queryset = Budget.active.all()
    paginate_by = 10


budget_list = BudgetListView.as_view()


class BudgetCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Budget
    template_name = 'budget/add.html'
    form_class = BudgetForm
    success_url = reverse_lazy('budget-list')
    success_message = _('Budget %(name)s was created successfuly!')


budget_add = BudgetCreateView.as_view()


class BudgetUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Budget
    template_name = 'budget/edit.html'
    form_class = BudgetForm
    success_url = reverse_lazy('budget-list')
    success_message = _('Budget %(name)s was updated successfuly!')


budget_edit = BudgetUpdateView.as_view()


class BudgetDeleteView(LoginRequiredMixin, DeleteView):
    model = Budget
    template_name = "budget/delete.html"
    success_url = reverse_lazy('budget-list')


budget_delete = BudgetDeleteView.as_view()


class BudgetEstimateListView(LoginRequiredMixin, ListView):
    model = BudgetEstimate
    template_name = "estimate/list.html"
    context_object_name = 'estimates'
    queryset = BudgetEstimate.active.select_related().all()
    paginate_by = 10

    def get_context_data(self, *args, **kwargs):
        context = super(BudgetEstimateListView, self).get_context_data(*args, **kwargs)
        budget_slug = self.kwargs.get('slug', None)
        budget = get_object_or_404(Budget.active.all(), slug=budget_slug)
        context['budget'] = budget
        return context


estimate_list = BudgetEstimateListView.as_view()


class BudgetEstimateCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = BudgetEstimate
    template_name = "estimate/add.html"
    form_class = BudgetEstimateForm
    success_url = reverse_lazy('budget-list')
    success_message = _('Estimate was created successfuly!')

    def form_valid(self, form):
        budget_slug = self.kwargs.get('slug', None)
        budget = get_object_or_404(Budget.active.all(), slug=budget_slug)
        form.save(commit=False)
        form.instance.budget = budget
        return super(BudgetEstimateCreateView, self).form_valid(form)


estimate_add = BudgetEstimateCreateView.as_view()


class BudgetEstimateUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = BudgetEstimate
    template_name = 'estimate/edit.html'
    form_class = BudgetEstimateForm
    success_url = reverse_lazy('budget-list')
    success_message = _('Estimate was updated successfuly!')
    context_object_name = 'estimate'


estimate_edit = BudgetEstimateUpdateView.as_view()


class BudgetEstimateDeleteView(LoginRequiredMixin, DeleteView):
    model = BudgetEstimate
    template_name = "estimate/delete.html"
    success_url = reverse_lazy('budget-list')
    context_object_name = 'estimate'


estimate_delete = BudgetEstimateDeleteView.as_view()
