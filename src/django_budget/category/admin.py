from __future__ import unicode_literals

from django.contrib import admin

from .models import Category


class CategoryAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields': ('name', 'slug'),
        }),
        ('Metadata', {
            'classes': ('collapse',),
            'fields': ('created', 'updated', 'is_deleted')
        })
    )
    list_display = ('name', 'is_deleted')
    list_filter = ('is_deleted',)
    prepopulated_fields = {
        'slug': ('name',),
    }
    search_fields = ('name',)


admin.site.register(Category, CategoryAdmin)
