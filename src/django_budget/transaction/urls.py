from django.urls import re_path
from django_budget.transaction.views import transaction_list, transaction_add, transaction_edit, transaction_delete

urlpatterns = [
    re_path(r'^$', transaction_list, name="transaction-list"),
    re_path(r'^add/$', transaction_add, name="transaction-add"),
    re_path(r'^edit/(?P<pk>\d+)/$', transaction_edit, name="transaction-edit"),
    re_path(r'^delete/(?P<pk>\d+)/$', transaction_delete, name="transaction-delete"),
]
