from __future__ import unicode_literals

from django.urls import re_path
from django_budget.summary.views import summary_list, summary_year, summary_month

urlpatterns = [
    re_path(r'^$', summary_list, name="summary-list"),
    re_path(r'^(?P<year>\d{4})/$', summary_year, name="summary-year"),
    re_path(r'^(?P<year>\d{4})/(?P<month>\d{1,2})/$', summary_month, name="summary-month")
]
