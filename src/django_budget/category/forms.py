from __future__ import unicode_literals

from django import forms
from django.template.defaultfilters import slugify

from django_budget.category.models import Category


class CategoryForm(forms.ModelForm):

    class Meta:
        model = Category
        fields = ('name',)

    def save(self):
        if not self.instance.slug:
            self.instance.slug = slugify(self.cleaned_data['name'])
        return super(CategoryForm, self).save()
