from __future__ import unicode_literals

from decimal import Decimal, InvalidOperation

from django import template
from django.conf import settings

register = template.Library()

# To override, copy to your settings file. Make sure to keep the tuples in
# descending order by percentage.
BUDGET_DEFAULT_CSS_PERCENTAGE = (
    # (percentage, CSS color class)
    (1.00, 'danger'),
    (0.75, 'warning'),
    (0.0, 'success'))

BUDGET_CSS_PERCENTAGE = getattr(settings,
                                'BUDGET_CSS_PERCENTAGE',
                                BUDGET_DEFAULT_CSS_PERCENTAGE)


@register.simple_tag()
def colorize_amount(estimate_amount, actual_amount):
    try:
        percentage = actual_amount / estimate_amount

    except (ZeroDivisionError, InvalidOperation):
        return ''

    for css_percentage, css_class in BUDGET_CSS_PERCENTAGE:
        css_percentage = make_decimal(css_percentage)

        if percentage >= css_percentage:
            return css_class


def make_decimal(amount):
    """
    If it's not a Decimal, it should be...
    """
    if not isinstance(amount, Decimal):
        amount = Decimal(str(amount))

    return amount
