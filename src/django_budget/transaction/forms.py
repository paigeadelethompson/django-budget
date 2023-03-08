from __future__ import unicode_literals

from django import forms
from django.utils.translation import gettext_lazy as _

from crispy_forms.bootstrap import PrependedText
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Field, Layout

from django_budget.base.forms import DatePickerInput
from .models import Transaction


class TransactionForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(TransactionForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.disable_csrf = True
        self.helper.label_class = 'col-md-2'
        self.helper.field_class = 'col-md-6'
        self.helper.layout = Layout(
            Field('transaction_type'),
            Field('category'),
            PrependedText('amount', _('$')),
            PrependedText('date', '<i class="glyphicon glyphicon-calendar"></i>'),
            Field('notes'))

    class Meta:
        exclude = []
        model = Transaction
        widgets = {'date': DatePickerInput()}
