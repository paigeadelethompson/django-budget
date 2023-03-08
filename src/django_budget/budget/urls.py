from django_budget.budget.views import budget_list, budget_add, budget_edit, budget_delete, estimate_add, estimate_edit, estimate_delete, estimate_list
from django.urls import re_path

urlpatterns = [
    re_path(r'^$', budget_list, name="budget-list"),
    re_path(r'^add/$', budget_add, name="budget-add"),
    re_path(r'^edit/(?P<slug>[\w-]+)/$', budget_edit, name="budget-edit"),
    re_path(r'^delete/(?P<slug>[\w-]+)/$', budget_delete, name="budget-delete"),
    re_path(r'^(?P<slug>[\w-]+)/estimate/$', estimate_list, name="estimate-list"),
    re_path(r'^(?P<slug>[\w-]+)/estimate/add/$', estimate_add, name="estimate-add"),
    re_path(r'^(?P<slug>[\w-]+)/estimate/edit/(?P<pk>\d+)/$', estimate_edit, name="estimate-edit"),
    re_path(r'^(?P<slug>[\w-]+)/estimate/delete/(?P<pk>\d+)/$', estimate_delete, name="estimate-delete")
]
