from __future__ import unicode_literals

from django import forms
from django.template.defaultfilters import slugify
from django.utils.translation import gettext_lazy as _

from crispy_forms.bootstrap import PrependedText
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Field, Layout

from django_budget.base.forms import DatePickerInput
from .models import Budget, BudgetEstimate


class BudgetForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(BudgetForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.disable_csrf = True
        self.helper.layout = Layout(
            Field('name'),
            PrependedText('start_date',
                          '<i class="glyphicon glyphicon-calendar"></i>'))

    def save(self):
        if not self.instance.slug:
            self.instance.slug = slugify(self.cleaned_data['name'])
        return super(BudgetForm, self).save()

    class Meta:
        model = Budget
        fields = ('name', 'start_date')
        widgets = {'start_date': DatePickerInput()}


class BudgetEstimateForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(BudgetEstimateForm, self).__init__(*args, **kwargs)
        self.fields['amount'].localize = True

        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.disable_csrf = True
        self.helper.layout = Layout(
            Field('category'),
            PrependedText('amount', _('$')))

    class Meta:
        model = BudgetEstimate
        fields = ('category', 'amount')
