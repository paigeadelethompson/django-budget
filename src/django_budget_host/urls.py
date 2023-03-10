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

import mfa
import mfa.TrustedDevice
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth import authenticate,login
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView
from django.contrib import messages

from django_ratelimit.decorators import ratelimit


class MyLoginView(LoginView):
    redirect_authenticated_user = True

    @ratelimit(key='ip')
    def login(request):
        context={}
        if request.method=="POST":
            username=request.POST["username"]
            password=request.POST["password"]
            user=authenticate(username=username,password=password)
            if user:
                from mfa.helpers import has_mfa
                res = has_mfa(username = username, request = request)
                if res:
                    return res
                return MyLoginView.create_session(request,user.username)
            context["invalid"]=True
        return render(request, "login.html", context)

    def create_session(request,username):
        user=User.objects.get(username=username)
        user.backend='django.contrib.auth.backends.ModelBackend'
        login(request, user)
        return HttpResponseRedirect(reverse('home'))
    
    def form_invalid(self, form):
        messages.error(self.request,'Invalid username or password')
        return self.render_to_response(self.get_context_data(form=form))

urlpatterns = [
    re_path(r'^$', dashboard, name='dashboard'),
    re_path(r'^admin/login/$', MyLoginView.as_view(), name='login'),
    re_path(r'^admin/logout/$', LogoutView.as_view(), name='logout'),
    re_path(r'^accounts/login/$', MyLoginView.as_view(), name='login'),
    re_path(r'^accounts/logout/$', LogoutView.as_view(), name='logout'),
    re_path(r'^accounts/profile/$', dashboard, name='profile'),
    re_path(r'^dashboard/$', dashboard, name='dashboard'),
    re_path(r'^setup/$', setup, name='setup'),
    path("admin/", admin.site.urls),
    path("budget/", include(django_budget.budget.urls), name="index"),
    path("budget/category/", include(django_budget.category.urls)),
    path("budget/summary/", include(django_budget.summary.urls)),
    path("budget/transaction/", include(django_budget.transaction.urls)),
    re_path(r'^mfa/', include('mfa.urls')),
    re_path(r'devices/add$', mfa.TrustedDevice.add,name="mfa_add_new_trusted_device"),
]
