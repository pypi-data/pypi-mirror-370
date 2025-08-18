import json
import logging

from django.core.exceptions import FieldDoesNotExist
from django.db.models import Q
from rest_framework.filters import BaseFilterBackend

logger = logging.getLogger(__name__)


class JqGridFilterBackend(BaseFilterBackend):
    """
    Custom filter backend for handling jqGrid filter requests.
    This enables advanced filtering directly from jqGrid filter toolbar and search dialog.
    """

    def filter_queryset(self, request, queryset, view):
        # Get filter parameters from request
        filters = request.query_params.get('filters', None)
        search = request.query_params.get('_search', 'false')

        # Skip if not searching
        if search != 'true' or not filters:
            return queryset

        try:
            # Parse the filters string into JSON
            filters_dict = json.loads(filters)
            allowed_fields = getattr(view, 'allowed_filters', [])

            # Build the filter Q object
            filter_q = self.build_filter_query(filters_dict, view, queryset.model, allowed_fields)
            if filter_q:
                queryset = queryset.filter(filter_q)

        except json.JSONDecodeError:
            logger.warning("Invalid JSON in jqGrid filter")
        except Exception as e:
            logger.error(f"JqGrid filter error: {str(e)}")

        return queryset

    def build_filter_query(self, filters_dict, view, model, allowed_fields):
        """
        Build a Q object from filter dictionary.
        Supports both simple filters and complex grouping operations.
        """
        filter_q = Q()
        filter_mappings = getattr(view, 'filter_mappings', {})

        def is_allowed(field):
            return field in allowed_fields or field in filter_mappings

        group_op = filters_dict.get('groupOp', 'AND').upper()

        # Handle complex grouping operations
        for group in filters_dict.get('groups', []):
            group_q = self.build_filter_query(group, view, model, allowed_fields)
            if group_op == 'AND':
                filter_q &= group_q
            else:  # OR
                filter_q |= group_q

        # Handle simple filter rules
        for rule in filters_dict.get('rules', []):
            field = rule.get('field', '')
            data = rule.get('data', '')
            op = rule.get('op', '')

            if not field or not op or not is_allowed(field):
                continue

            # Map jqGrid operator to Django filter
            filter_expr = self.map_operator(field, op, data, filter_mappings, model)
            if not filter_expr:
                continue

            field_name, field_value = filter_expr

            # Check if operator is negated
            rule_q = ~Q(**{field_name: field_value}) if op in ['ne', 'nc', 'bn', 'en', 'ni', 'nn'] else Q(
                **{field_name: field_value})

            # Combine with existing query based on group operator
            if group_op == 'AND':
                filter_q &= rule_q
            else:  # OR
                filter_q |= rule_q

        return filter_q

    def map_operator(self, field, op, data, filter_mappings, model):
        """
        Map jqGrid operators to Django query expressions.
        Returns a tuple of (field_name, value) to be used in a Q object.
        """
        # Check if a custom mapping exists
        custom_key = f"{field}__jq_{op}"
        if custom_key in filter_mappings:
            return (filter_mappings[custom_key], data)

        # Standard operator mappings
        ops = {
            "eq": "__exact",  # equals - fixed to use __exact
            "ne": "__exact",  # not equals - fixed to use __exact
            "lt": "__lt",  # less than
            "le": "__lte",  # less than or equal
            "gt": "__gt",  # greater than
            "ge": "__gte",  # greater than or equal
            "cn": "__icontains",  # contains
            "nc": "__icontains",  # not contains
            "bw": "__istartswith",  # begins with
            "bn": "__istartswith",  # not begins with
            "ew": "__iendswith",  # ends with
            "en": "__iendswith",  # not ends with
            "in": "__in",  # is in
            "ni": "__in",  # is not in
            "nu": "__isnull",  # is null
            "nn": "__isnull"  # is not null
        }

        suffix = ops.get(op)
        if suffix is None:  # Check for None instead of falsy value
            return None

        field_lookup = f"{field}{suffix}"

        try:
            # Get the field object for type casting
            field_obj = model._meta.get_field(field.split('__')[0])
        except FieldDoesNotExist:
            return None

        # Special handling for different operators
        if op in ['nu', 'nn']:
            return (field_lookup, op == 'nu')
        elif op in ['in', 'ni']:
            values = [self.cast_value(field_obj, v.strip()) for v in data.split(',')]
            return (field_lookup, values)
        else:
            return (field_lookup, self.cast_value(field_obj, data))

    def cast_value(self, field, value):
        """
        Cast string values to appropriate Python types based on field type.
        """
        from django.db.models import IntegerField, BooleanField, FloatField, DateField, DateTimeField, JSONField

        try:
            if isinstance(field, IntegerField):
                return int(value)
            if isinstance(field, FloatField):
                return float(value)
            if isinstance(field, BooleanField):
                return value.lower() in ['true', '1', 'yes', 'on']
            if isinstance(field, (DateField, DateTimeField)):
                from django.utils.dateparse import parse_date, parse_datetime
                return parse_datetime(value) or parse_date(value)
            # Additional handling for JSONField could be added here
            return value
        except Exception:
            # Return the original value if casting fails
            return value


class JqGridSortBackend(BaseFilterBackend):
    """
    Custom sort backend for handling jqGrid sorting requests.
    Supports multi-column sorting.
    """

    def filter_queryset(self, request, queryset, view):
        # Get sorting parameters
        sidx = request.query_params.get('sidx', '')
        sord = request.query_params.get('sord', 'asc')

        # Check if we need to sort
        if not sidx:
            return queryset

        allowed_fields = getattr(view, 'allowed_sort_fields', [])

        # Handle multi-column sorting
        sort_fields = []

        if ',' in sidx:
            # Multiple sort fields
            field_list = sidx.split(',')
            for field_order in field_list:
                # Split field and direction, handling spaces properly
                split = [x for x in field_order.strip().split(' ') if x != '']
                field = split[0]
                direction = split[1] if len(split) > 1 else sord

                # Skip fields not in allowed list
                if allowed_fields and field not in allowed_fields:
                    continue

                # Add direction prefix for descending order
                if direction.lower() == 'desc':
                    sort_fields.append(f"-{field}")
                else:
                    sort_fields.append(field)
        else:
            # Single field sorting
            field = sidx

            # Skip if not in allowed list
            if allowed_fields and field not in allowed_fields:
                return queryset

            if sord.lower() == 'desc':
                sort_fields.append(f"-{field}")
            else:
                sort_fields.append(field)

        # Apply ordering if we have valid sort fields
        if sort_fields:
            return queryset.order_by(*sort_fields)

        return queryset