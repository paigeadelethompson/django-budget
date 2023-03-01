from __future__ import unicode_literals

from django import forms


class DatePickerInput(forms.widgets.DateInput):
    attrs = {'class': "datepicker",
             'data-date-format': 'dd/mm/yyyy'}

    def __init__(self):
        super(DatePickerInput, self).__init__(self.attrs, format='%d/%m/%Y')
