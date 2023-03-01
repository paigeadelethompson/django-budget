from __future__ import unicode_literals

from django import template
from django.urls import reverse, NoReverseMatch
register = template.Library()


@register.simple_tag(takes_context=True)
def navactive(context, url, css_class='active'):
    try:
        if context['request'].path == reverse(url):
            return css_class

    except NoReverseMatch:
        pass

    return ''


@register.simple_tag(takes_context=True)
def pagactive(context, page_number):
    if context['request'].GET.get('page') == str(page_number):
        return 'active'

    return ''
