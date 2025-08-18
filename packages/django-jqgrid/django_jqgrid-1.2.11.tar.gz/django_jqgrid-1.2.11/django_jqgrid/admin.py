from django.contrib import admin
from django import forms

from django_jqgrid.models import GridFilter

try:
    from jsoneditor.forms import JSONEditor
    HAS_JSON_EDITOR = True
except ImportError:
    HAS_JSON_EDITOR = False


class GridFilterForm(forms.ModelForm):
    class Meta:
        model = GridFilter
        fields = '__all__'
        if HAS_JSON_EDITOR:
            widgets = {
                'value': JSONEditor()
            }
        else:
            widgets = {
                'value': forms.Textarea(attrs={'rows': 5, 'cols': 80})
            }

@admin.register(GridFilter)
class GridFilterAdmin(admin.ModelAdmin):
    form = GridFilterForm
    list_display = ('name', 'key', 'table', 'created_by', 'is_global', 'created_at')
    list_filter = ('key', 'is_global', 'table', 'created_by')
    search_fields = ('name', 'value')
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (None, {
            'fields': ('name', 'key', 'table', 'created_by', 'is_global')
        }),
        ('Data', {
            'fields': ('value',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
