from __future__ import unicode_literals

from django.urls import reverse_lazy
from django.views.generic import RedirectView, TemplateView

from braces.views import LoginRequiredMixin


class BudgetSetupView(LoginRequiredMixin, TemplateView):
    template_name = "setup.html"


setup = BudgetSetupView.as_view()


class IndexRedirectView(LoginRequiredMixin, RedirectView):
    url = reverse_lazy('dashboard')


index = IndexRedirectView.as_view()
