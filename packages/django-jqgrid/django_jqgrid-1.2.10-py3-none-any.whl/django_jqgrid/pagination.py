from django.core.paginator import Paginator
from django.utils.functional import cached_property
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class OptimizedPaginator(Paginator):
    """Optimized paginator that avoids unnecessary count queries."""
    
    @cached_property
    def count(self):
        """Override count to use cached value if available."""
        if hasattr(self.object_list, '_result_cache') and self.object_list._result_cache is not None:
            return len(self.object_list._result_cache)
        return super().count


class JqGridPagination(PageNumberPagination):
    page_query_param = 'page'
    page_size_query_param = 'rows'  # Align with jqGrid param
    page_size = 25
    max_page_size = 5000
    django_paginator_class = OptimizedPaginator

    def get_paginated_response(self, data):
        # Allow views to optionally add footer/summary data
        userdata = getattr(self, 'userdata', {})

        return Response({
            'page': self.page.number,
            'total_pages': self.page.paginator.num_pages,
            'records': self.page.paginator.count,  # Renamed for jqGrid compatibility
            'userdata': userdata,
            'data': data
        })

    def get_paginated_response_schema(self, schema):
        return {
            'type': 'object',
            'properties': {
                'page': {'type': 'integer', 'example': 1},
                'total_pages': {'type': 'integer', 'example': 10},
                'records': {'type': 'integer', 'example': 250},
                'userdata': {'type': 'object'},
                'data': {
                    'type': 'array',
                    'items': schema
                }
            }
        }
