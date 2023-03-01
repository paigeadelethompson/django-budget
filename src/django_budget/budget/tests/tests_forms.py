from __future__ import unicode_literals

from datetime import date
from decimal import Decimal

from django.test import TestCase

from model_mommy import mommy


class BudgetFormTest(TestCase):

    def test_form_save(self):
        from budget.forms import BudgetForm

        form_data = {'name': 'foo',
                     'start_date': date.today()}
        form = BudgetForm(data=form_data)

        self.assertTrue(form.is_valid())

    def test_form_save_should_populate_slug_field(self):
        from budget.forms import BudgetForm

        form_data = {'name': 'Foo Bar',
                     'start_date': date.today()}
        form = BudgetForm(data=form_data)

        self.assertTrue(form.is_valid())

        form.save()
        self.assertEqual('foo-bar', form.instance.slug)


class BudgetEstimateForm(TestCase):

    def test_form_save(self):
        from budget.forms import BudgetEstimateForm

        category = mommy.make('Category')
        form_data = {'category': category.id, 'amount': Decimal('1.0')}
        form = BudgetEstimateForm(data=form_data)

        self.assertTrue(form.is_valid())

    def test_deleted_category_should_not_show_in_estimate_form(self):
        from budget.forms import BudgetEstimateForm

        category = mommy.make('Category', is_deleted=True)
        form = BudgetEstimateForm()

        self.assertNotIn((category.id, category.name), form.fields['category'].choices)
