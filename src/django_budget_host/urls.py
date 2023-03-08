from django.contrib import admin
from django.urls import path, include, re_path
from django.contrib import admin

import django_budget.budget.urls
import django_budget.category.urls
import django_budget.summary.urls
import django_budget.transaction.urls

from django_budget.dashboard.views import dashboard
from django_budget.base.views import setup

from django.contrib.auth.views import LoginView, LogoutView

urlpatterns = [
    re_path(r'^$', dashboard, name='dashboard'),
    re_path(r'^accounts/login/$', LoginView.as_view(), name='login'),
    re_path(r'^accounts/logout/$', LogoutView.as_view(), name='logout'),
    re_path(r'^accounts/profile/$', dashboard, name='profile'),
    re_path(r'^dashboard/$', dashboard, name='dashboard'),
    re_path(r'^setup/$', setup, name='setup'),
    path("admin/", admin.site.urls),
    path("budget/", include(django_budget.budget.urls), name="index"),
    path("budget/category/", include(django_budget.category.urls)),
    path("budget/summary/", include(django_budget.summary.urls)),
    path("budget/transaction/", include(django_budget.transaction.urls)),
]
