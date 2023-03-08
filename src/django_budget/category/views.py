from __future__ import unicode_literals

from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView
from django.utils.translation import gettext_lazy as _

from braces.views import LoginRequiredMixin

from .forms import CategoryForm
from .models import Category


class CategoryListView(LoginRequiredMixin, ListView):
    model = Category
    template_name = 'category/list.html'
    context_object_name = 'categories'
    queryset = Category.active.all()
    paginate_by = 10


category_list = CategoryListView.as_view()


class CategoryCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Category
    template_name = 'category/add.html'
    form_class = CategoryForm
    success_url = reverse_lazy('category-list')
    success_message = _('Category %(name)s was created successfully!')


category_add = CategoryCreateView.as_view()


class CategoryUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Category
    template_name = 'category/edit.html'
    form_class = CategoryForm
    success_url = reverse_lazy('category-list')
    success_message = _('Category %(name)s was updated successfully!')


category_edit = CategoryUpdateView.as_view()


class CategoryDeleteView(LoginRequiredMixin, DeleteView):
    model = Category
    template_name = 'category/delete.html'
    success_url = reverse_lazy('category-list')


category_delete = CategoryDeleteView.as_view()
