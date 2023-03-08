from django.urls import re_path
from django_budget.category.views import category_list, category_add, category_edit, category_delete

urlpatterns = [
    re_path(r'^$', category_list, name="category-list"),
    re_path(r'^add/$', category_add, name="category-add"),
    re_path(r'^edit/(?P<slug>[\w_-]+)/$', category_edit, name="category-edit"),
    re_path(r'^delete/(?P<slug>[\w_-]+)/$', category_delete, name="category-delete"),
]
