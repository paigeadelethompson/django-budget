from __future__ import unicode_literals

from django.urls import reverse as reverse
from django.db import models
from django.utils.translation import gettext_lazy as _
from six import python_2_unicode_compatible

from django_budget.base.models import ActiveManager, StandardMetadata


@python_2_unicode_compatible
class Category(StandardMetadata):
    """
    Categories are the means to loosely tie together the transactions and
    estimates.

    They are used to aggregate transactions together and compare them to the
    appropriate budget estimate. For the reasoning behind this, the docstring
    on the Transaction object explains this.
    """
    name = models.CharField(_('Name'), max_length=100)
    slug = models.SlugField(_('Slug'), unique=True)

    objects = models.Manager()
    active = ActiveManager()

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('category-edit', args=[self.slug])

    class Meta:
        verbose_name = _('Category')
        verbose_name_plural = _('Categories')
