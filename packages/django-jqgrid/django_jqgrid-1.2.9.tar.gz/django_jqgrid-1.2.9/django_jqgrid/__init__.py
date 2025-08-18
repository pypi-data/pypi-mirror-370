# This file marks the directory as a Python package.
# Version information
__version__ = '1.2.9'

# Package metadata
__author__ = 'Django jqGrid Team'
__email__ = 'support@django-jqgrid.org'
__description__ = 'A Django app for integrating jqGrid with Django REST Framework'

# Default Django app configuration
default_app_config = 'django_jqgrid.apps.DjangoJqgridConfig'

# Import key components for easier access
# Use lazy imports to avoid "Apps aren't loaded yet" error
def __getattr__(name):
    if name == 'JqGridConfigMixin':
        from .mixins import JqGridConfigMixin
        return JqGridConfigMixin
    elif name == 'JqGridBulkActionMixin':
        from .mixins import JqGridBulkActionMixin
        return JqGridBulkActionMixin
    elif name == 'GridFilterViewSet':
        from .views import GridFilterViewSet
        return GridFilterViewSet
    elif name == 'JqGridFilterBackend':
        from .filters import JqGridFilterBackend
        return JqGridFilterBackend
    elif name == 'JqGridOrderingFilter':
        from .ordering import JqGridOrderingFilter
        return JqGridOrderingFilter
    raise AttributeError(f"module {__name__} has no attribute {name}")

__all__ = [
    'JqGridConfigMixin',
    'JqGridBulkActionMixin', 
    'GridFilterViewSet',
    'JqGridFilterBackend',
    'JqGridOrderingFilter',
]
