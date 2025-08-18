"""
Custom ordering filter for jqGrid compatibility
"""
from rest_framework.filters import OrderingFilter


class JqGridOrderingFilter(OrderingFilter):
    """
    Custom ordering filter that handles jqGrid's sorting parameters.
    
    jqGrid sends:
    - sidx: field name(s) to sort by
    - sord: sort order (asc/desc)
    
    DRF OrderingFilter expects:
    - ordering: field names with optional '-' prefix for descending
    """
    
    def get_ordering(self, request, queryset, view):
        """
        Extract ordering from jqGrid parameters (sidx/sord) or fall back to standard ordering.
        """
        # First check for jqGrid parameters
        sidx = request.query_params.get('sidx', '').strip()
        sord = request.query_params.get('sord', 'asc').strip().lower()
        
        if sidx:
            # Handle multi-column sorting
            ordering = []
            
            if ',' in sidx:
                # Multiple sort fields
                fields = [f.strip() for f in sidx.split(',')]
                orders = [o.strip().lower() for o in sord.split(',')] if ',' in sord else [sord] * len(fields)
                
                # Ensure we have the same number of sort orders as fields
                while len(orders) < len(fields):
                    orders.append('asc')
                
                for field, order in zip(fields, orders):
                    if field:
                        # Validate field is in ordering_fields
                        valid_fields = self.get_valid_fields(queryset, view, {'request': request})
                        field_names = [f[1] for f in valid_fields]
                        
                        if field in field_names:
                            if order == 'desc':
                                ordering.append(f'-{field}')
                            else:
                                ordering.append(field)
            else:
                # Single field sorting
                valid_fields = self.get_valid_fields(queryset, view, {'request': request})
                field_names = [f[1] for f in valid_fields]
                
                if sidx in field_names:
                    if sord == 'desc':
                        ordering = [f'-{sidx}']
                    else:
                        ordering = [sidx]
            
            if ordering:
                return ordering
        
        # Fall back to standard ordering parameter if no jqGrid params
        return super().get_ordering(request, queryset, view)
    
    def filter_queryset(self, request, queryset, view):
        """
        Filter the queryset based on ordering parameters.
        """
        ordering = self.get_ordering(request, queryset, view)
        
        if ordering:
            # Distinct is required when filtering across relationships
            distinct = False
            for order_field in ordering:
                field_name = order_field.lstrip('-')
                if '__' in field_name:
                    distinct = True
                    break
            
            queryset = queryset.order_by(*ordering)
            
            if distinct:
                # Ensure distinct results when sorting on related fields
                queryset = queryset.distinct()
        
        return queryset