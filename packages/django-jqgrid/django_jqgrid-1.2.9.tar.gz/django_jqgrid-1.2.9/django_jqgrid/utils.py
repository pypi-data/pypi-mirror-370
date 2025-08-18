"""Utility functions for django-jqgrid package."""

from django.contrib.contenttypes.models import ContentType
from django.core.cache import cache
from django.db import models
import json
import logging

logger = logging.getLogger(__name__)


def get_content_type_cached(app_label, model_name, cache_timeout=3600):
    """
    Get ContentType with caching to reduce database queries.
    
    Args:
        app_label: Django app label
        model_name: Model name
        cache_timeout: Cache timeout in seconds (default: 1 hour)
    
    Returns:
        ContentType instance or None
    """
    cache_key = f"django_jqgrid_ct_{app_label}_{model_name}"
    content_type = cache.get(cache_key)
    
    if content_type is None:
        try:
            content_type = ContentType.objects.get(app_label=app_label, model=model_name)
            cache.set(cache_key, content_type, cache_timeout)
        except ContentType.DoesNotExist:
            logger.warning(f"ContentType not found for {app_label}.{model_name}")
            return None
    
    return content_type


def parse_jqgrid_filters(filters_str):
    """
    Parse jqGrid filter string into Django ORM lookup format.
    
    Args:
        filters_str: JSON string containing jqGrid filters
    
    Returns:
        Dictionary of field lookups for Django ORM
    """
    if not filters_str:
        return {}
    
    try:
        filters = json.loads(filters_str)
    except json.JSONDecodeError:
        logger.error(f"Invalid filter JSON: {filters_str}")
        return {}
    
    if not isinstance(filters, dict) or 'rules' not in filters:
        return {}
    
    # Map jqGrid operators to Django lookups
    operator_map = {
        'eq': '',  # exact
        'ne': '__ne',
        'lt': '__lt',
        'le': '__lte',
        'gt': '__gt',
        'ge': '__gte',
        'cn': '__icontains',  # contains
        'nc': '__icontains',  # not contains (handled separately)
        'bw': '__istartswith',  # begins with
        'bn': '__istartswith',  # not begins with (handled separately)
        'ew': '__iendswith',  # ends with
        'en': '__iendswith',  # not ends with (handled separately)
        'in': '__in',
        'ni': '__in',  # not in (handled separately)
        'nu': '__isnull',  # is null
        'nn': '__isnull',  # not null (handled separately)
    }
    
    django_filters = {}
    exclude_filters = {}
    
    for rule in filters.get('rules', []):
        field = rule.get('field')
        op = rule.get('op')
        data = rule.get('data')
        
        if not field or not op:
            continue
        
        # Handle special cases
        if op in ['nu', 'nn']:
            value = True if op == 'nu' else False
            django_filters[f"{field}__isnull"] = value
        elif op in ['nc', 'bn', 'en', 'ni']:
            # These are "not" operators, use exclude
            base_op = op[1:]  # Remove 'n' prefix
            lookup = operator_map.get(base_op, '')
            exclude_filters[f"{field}{lookup}"] = data
        else:
            lookup = operator_map.get(op, '')
            django_filters[f"{field}{lookup}"] = data
    
    return {'filter': django_filters, 'exclude': exclude_filters}


def get_model_field_info(model, field_name):
    """
    Get detailed information about a model field.
    
    Args:
        model: Django model class
        field_name: Field name
    
    Returns:
        Dictionary with field information
    """
    try:
        field = model._meta.get_field(field_name)
        
        info = {
            'name': field_name,
            'type': field.__class__.__name__,
            'verbose_name': getattr(field, 'verbose_name', field_name),
            'help_text': getattr(field, 'help_text', ''),
            'max_length': getattr(field, 'max_length', None),
            'blank': getattr(field, 'blank', False),
            'null': getattr(field, 'null', False),
            'editable': getattr(field, 'editable', True),
            'primary_key': getattr(field, 'primary_key', False),
            'unique': getattr(field, 'unique', False),
        }
        
        # Add choices if available
        if hasattr(field, 'choices') and field.choices:
            info['choices'] = field.choices
        
        # Add relation info if it's a relation field
        if hasattr(field, 'related_model') and field.related_model:
            info['related_model'] = field.related_model.__name__
            info['related_app'] = field.related_model._meta.app_label
        
        return info
        
    except Exception as e:
        logger.error(f"Error getting field info for {model.__name__}.{field_name}: {e}")
        return None


def format_value_for_export(value, field_type=None):
    """
    Format a value for export (CSV, Excel, etc.).
    
    Args:
        value: The value to format
        field_type: Optional field type for specific formatting
    
    Returns:
        Formatted value as string
    """
    if value is None:
        return ''
    
    if isinstance(value, models.Model):
        return str(value)
    
    if isinstance(value, (list, tuple)):
        return ', '.join(str(v) for v in value)
    
    if isinstance(value, dict):
        return json.dumps(value)
    
    if isinstance(value, bool):
        return 'Yes' if value else 'No'
    
    return str(value)


def get_jqgrid_sort_params(request):
    """
    Extract and parse jqGrid sorting parameters from request.
    
    Args:
        request: Django request object
    
    Returns:
        List of ordering fields for Django ORM
    """
    sidx = request.GET.get('sidx', '').strip()
    sord = request.GET.get('sord', 'asc').strip()
    
    if not sidx:
        return []
    
    # Handle multi-column sorting
    if ',' in sidx:
        sort_fields = sidx.split(',')
        sort_orders = sord.split(',') if ',' in sord else [sord] * len(sort_fields)
        
        ordering = []
        for field, order in zip(sort_fields, sort_orders):
            field = field.strip()
            if field:
                prefix = '-' if order.lower() == 'desc' else ''
                ordering.append(f"{prefix}{field}")
        
        return ordering
    else:
        # Single column sorting
        prefix = '-' if sord.lower() == 'desc' else ''
        return [f"{prefix}{sidx}"]


def build_jqgrid_response(queryset, page, page_size, total_count=None):
    """
    Build a properly formatted jqGrid response.
    
    Args:
        queryset: The queryset or list of objects
        page: Current page number
        page_size: Number of items per page
        total_count: Optional total count (if not provided, will be calculated)
    
    Returns:
        Dictionary formatted for jqGrid
    """
    if total_count is None:
        total_count = queryset.count() if hasattr(queryset, 'count') else len(queryset)
    
    total_pages = (total_count + page_size - 1) // page_size if page_size > 0 else 1
    
    return {
        'page': page,
        'total_pages': total_pages,
        'records': total_count,
        'data': list(queryset),
        'userdata': {}  # Can be extended with summary data
    }
