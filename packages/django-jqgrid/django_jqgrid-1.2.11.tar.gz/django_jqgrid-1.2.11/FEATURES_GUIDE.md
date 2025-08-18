# Django jqGrid Features Guide

This guide provides comprehensive documentation on all available features in django-jqgrid and how to enable/configure them.

## Table of Contents

1. [Core Features](#core-features)
2. [Advanced Features](#advanced-features)
3. [Feature Flags](#feature-flags)
4. [ViewSet Configuration](#viewset-configuration)
5. [JavaScript Configuration](#javascript-configuration)
6. [Settings Configuration](#settings-configuration)

## Core Features

### 1. Basic Grid Display

**Enabled by default** when using `JqGridConfigMixin`.

```python
from django_jqgrid.mixins import JqGridConfigMixin
from rest_framework import viewsets

class ProductViewSet(JqGridConfigMixin, viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
```

### 2. Sorting

**Enabled by default** for all visible columns.

To customize:
```python
class ProductViewSet(JqGridConfigMixin, viewsets.ModelViewSet):
    # Specify which fields can be sorted
    ordering_fields = ['name', 'price', 'created_at']
    
    # Set default ordering
    ordering = ['-created_at']
```

### 3. Searching

Enable search toolbar:
```python
class ProductViewSet(JqGridConfigMixin, viewsets.ModelViewSet):
    # Enable search for specific fields
    search_fields = ['name', 'description', 'sku']
    
    # Enable filter toolbar (default: True)
    enable_filter_toolbar = True
```

### 4. Pagination

**Enabled by default** with customizable page sizes:
```python
class ProductViewSet(JqGridConfigMixin, viewsets.ModelViewSet):
    # Set available page size options
    page_size_options = [10, 25, 50, 100, 'All']
    
    # Set default page size
    page_size = 25
```

In settings.py:
```python
# Global defaults
JQGRID_DEFAULT_ROWS = 25
JQGRID_MAX_ROWS = 1000
```

## Advanced Features

### 1. Bulk Operations

Enable bulk actions by adding the mixin:
```python
from django_jqgrid.mixins import JqGridBulkActionMixin

class ProductViewSet(JqGridConfigMixin, JqGridBulkActionMixin, viewsets.ModelViewSet):
    # Specify which fields can be bulk updated
    bulk_updateable_fields = ['category', 'price', 'is_active']
    
    # Custom bulk actions (optional)
    bulk_actions = [
        {
            'id': 'bulk-delete',
            'label': 'Delete Selected',
            'icon': 'fa-trash',
            'class': 'btn-danger'
        },
        {
            'id': 'bulk-update',
            'label': 'Update Selected',
            'icon': 'fa-edit',
            'class': 'btn-primary'
        },
        {
            'id': 'custom-action',
            'label': 'Custom Action',
            'icon': 'fa-cog',
            'class': 'btn-info',
            'action': 'customBulkAction'  # JavaScript function name
        }
    ]
```

### 2. Inline Editing

Enable inline editing:
```python
class ProductViewSet(JqGridConfigMixin, viewsets.ModelViewSet):
    # Enable inline editing
    enable_inline_editing = True
    
    # Specify which fields are editable
    editable_fields = ['name', 'price', 'quantity', 'is_active']
    
    # Field-specific edit options
    jqgrid_field_overrides = {
        'price': {
            'editable': True,
            'edittype': 'text',
            'editoptions': {'size': 10},
            'editrules': {'required': True, 'number': True, 'minValue': 0}
        },
        'category': {
            'editable': True,
            'edittype': 'select',
            'editoptions': {
                'dataUrl': '/api/categories/',
                'buildSelect': 'buildCategorySelect'
            }
        }
    }
```

### 3. Cell Editing

Enable cell-by-cell editing:
```python
class ProductViewSet(JqGridConfigMixin, viewsets.ModelViewSet):
    # Enable cell editing
    enable_cell_editing = True
    
    # Additional cell edit configuration
    cell_edit_options = {
        'cellsubmit': 'remote',
        'cellurl': '/api/products/cell-update/'
    }
```

### 4. Grouping

Enable data grouping:
```python
class ProductViewSet(JqGridConfigMixin, viewsets.ModelViewSet):
    # Enable grouping feature
    enable_grouping = True
    
    # Specify groupable fields
    groupable_fields = ['category', 'status', 'brand']
    
    # Default grouping configuration
    default_grouping = {
        'field': 'category',
        'order': 'asc',
        'groupText': ['<b>{0} - {1} Item(s)</b>'],
        'groupCollapse': False,
        'groupSummary': [True]
    }
    
    # Aggregation options for grouped data
    aggregation_fields = {
        'price': ['min', 'max', 'avg'],
        'quantity': ['sum'],
        'id': ['count']
    }
```

### 5. Frozen Columns

Keep columns fixed while scrolling:
```python
class ProductViewSet(JqGridConfigMixin, viewsets.ModelViewSet):
    # Specify columns to freeze
    frozen_columns = ['id', 'name']
    
    # Enable frozen columns feature
    enable_frozen_columns = True
```

### 6. Subgrids

Enable nested subgrids:
```python
class OrderViewSet(JqGridConfigMixin, viewsets.ModelViewSet):
    # Enable subgrid
    enable_subgrid = True
    
    # Subgrid configuration
    subgrid_config = {
        'url': '/api/orders/{id}/items/',
        'model': 'OrderItem',
        'columns': ['product', 'quantity', 'price', 'total']
    }
    
    @action(detail=True, methods=['get'])
    def items(self, request, pk=None):
        """Return items for a specific order."""
        order = self.get_object()
        items = order.items.all()
        serializer = OrderItemSerializer(items, many=True)
        return Response(serializer.data)
```

### 7. Tree Grid

Display hierarchical data:
```python
class CategoryViewSet(JqGridConfigMixin, viewsets.ModelViewSet):
    # Enable tree grid
    enable_tree_grid = True
    
    # Tree grid configuration
    tree_config = {
        'tree_field': 'name',
        'level_field': 'level',
        'parent_field': 'parent_id',
        'leaf_field': 'is_leaf',
        'expanded_field': 'expanded'
    }
```

### 8. Export Features

Enable data export:
```python
class ProductViewSet(JqGridConfigMixin, viewsets.ModelViewSet):
    # Enable export buttons
    enable_export = True
    
    # Specify export formats
    export_formats = ['excel', 'csv', 'pdf']
    
    # Custom export configuration
    export_config = {
        'excel': {
            'filename': 'products_{date}.xlsx',
            'include_headers': True,
            'freeze_headers': True
        },
        'csv': {
            'filename': 'products_{date}.csv',
            'delimiter': ',',
            'include_headers': True
        }
    }
```

### 9. Import Features

Enable data import:
```python
class ProductViewSet(JqGridConfigMixin, viewsets.ModelViewSet):
    # Enable import functionality
    enable_import = True
    
    # Import configuration
    import_config = {
        'allowed_formats': ['xlsx', 'csv'],
        'preview_rows': 10,
        'batch_size': 100,
        'update_existing': True,
        'unique_fields': ['sku']
    }
    
    @action(detail=False, methods=['post'])
    def import_data(self, request):
        """Handle file import."""
        # Implementation provided by mixin
        return super().import_data(request)
```

### 10. Column Chooser

Allow users to show/hide columns:
```python
class ProductViewSet(JqGridConfigMixin, viewsets.ModelViewSet):
    # Enable column chooser
    enable_column_chooser = True
    
    # Default visible columns
    visible_columns = ['id', 'name', 'price', 'stock']
    
    # All available columns
    available_columns = ['id', 'name', 'sku', 'price', 'cost', 
                        'stock', 'category', 'created_at', 'updated_at']
```

### 11. Filter Saving

Save and load custom filters:
```python
class ProductViewSet(JqGridConfigMixin, viewsets.ModelViewSet):
    # Enable filter saving
    enable_filter_save = True
    
    # Use per-user filters
    user_specific_filters = True
```

### 12. Real-time Updates

Enable WebSocket updates:
```python
class ProductViewSet(JqGridConfigMixin, viewsets.ModelViewSet):
    # Enable real-time updates
    enable_realtime_updates = True
    
    # WebSocket configuration
    websocket_config = {
        'channel': 'products',
        'update_interval': 5000,  # milliseconds
        'update_method': 'merge'  # 'merge' or 'replace'
    }
```

## Feature Flags

### Global Feature Flags (settings.py)

```python
# Enable/disable features globally
JQGRID_FEATURES = {
    'ENABLE_BULK_OPERATIONS': True,
    'ENABLE_INLINE_EDITING': True,
    'ENABLE_CELL_EDITING': False,
    'ENABLE_GROUPING': True,
    'ENABLE_FROZEN_COLUMNS': True,
    'ENABLE_EXPORT': True,
    'ENABLE_IMPORT': True,
    'ENABLE_COLUMN_CHOOSER': True,
    'ENABLE_FILTER_SAVE': True,
    'ENABLE_REALTIME_UPDATES': False,
    'ENABLE_THEMES': True,
    'ENABLE_RESPONSIVE_MODE': True,
}

# Theme configuration
JQGRID_THEME = 'bootstrap4'  # Options: 'bootstrap', 'bootstrap4', 'bootstrap5', 'jqueryui'
JQGRID_ICON_SET = 'fontAwesome'  # Options: 'fontAwesome', 'bootstrap', 'jQueryUI', 'glyph'

# Performance settings
JQGRID_ENABLE_OPTIMIZATION = True
JQGRID_CACHE_TIMEOUT = 300  # seconds
JQGRID_USE_SELECT2 = True  # Enhanced dropdowns
```

### Per-ViewSet Feature Control

```python
class ProductViewSet(JqGridConfigMixin, viewsets.ModelViewSet):
    # Override global settings for this viewset
    jqgrid_features = {
        'enable_bulk_operations': True,
        'enable_inline_editing': False,
        'enable_export': True,
        'enable_grouping': True,
    }
```

## JavaScript Configuration

### Global JavaScript Configuration

```javascript
// Configure jqGrid globally
window.jqGridConfig = {
    // Default options for all grids
    defaultGridOptions: {
        datatype: 'json',
        mtype: 'GET',
        height: 'auto',
        autowidth: true,
        responsive: true,
        styleUI: 'Bootstrap4',
        iconSet: 'fontAwesome'
    },
    
    // Feature flags
    features: {
        enableTooltips: true,
        enableKeyboardNavigation: true,
        enableContextMenu: true,
        enableDragAndDrop: false,
        enableAutoSave: false
    },
    
    // Custom hooks
    hooks: {
        beforeInitGrid: function(tableInstance) {
            // Custom initialization logic
        },
        afterInitGrid: function(tableInstance) {
            // Post-initialization logic
        }
    }
};
```

### Per-Grid Configuration

```javascript
// Initialize grid with custom options
window.initializeTableInstance('productGrid', 'example', 'product', {
    features: {
        enableGrouping: true,
        enableFrozenColumns: true,
        enableColumnReordering: true
    },
    
    // Custom event handlers
    onSelectRow: function(rowid, status) {
        console.log('Row selected:', rowid);
    },
    
    // Custom toolbar buttons
    customButtons: [
        {
            id: 'refresh-data',
            label: 'Refresh',
            icon: 'fa-sync',
            action: function(tableInstance) {
                tableInstance.$grid.trigger('reloadGrid');
            }
        }
    ]
});
```

## Conditional Features

### Role-Based Features

```python
class ProductViewSet(JqGridConfigMixin, viewsets.ModelViewSet):
    def get_jqgrid_features(self):
        """Enable features based on user role."""
        features = super().get_jqgrid_features()
        
        if self.request.user.is_staff:
            features['enable_bulk_operations'] = True
            features['enable_inline_editing'] = True
            features['enable_import'] = True
        else:
            features['enable_bulk_operations'] = False
            features['enable_inline_editing'] = False
            features['enable_import'] = False
            
        return features
    
    def get_visible_columns(self):
        """Show columns based on permissions."""
        columns = ['id', 'name', 'price', 'stock']
        
        if self.request.user.has_perm('view_cost'):
            columns.extend(['cost', 'profit_margin'])
            
        if self.request.user.is_superuser:
            columns.extend(['created_by', 'updated_by'])
            
        return columns
```

### Dynamic Feature Loading

```python
class ProductViewSet(JqGridConfigMixin, viewsets.ModelViewSet):
    def get_context_data(self, **kwargs):
        """Pass feature flags to template."""
        context = super().get_context_data(**kwargs)
        
        # Check user preferences
        user_prefs = self.request.user.preferences
        
        context['features'] = {
            'theme': user_prefs.get('grid_theme', 'bootstrap4'),
            'page_size': user_prefs.get('default_page_size', 25),
            'enable_tooltips': user_prefs.get('show_tooltips', True),
            'enable_shortcuts': user_prefs.get('keyboard_shortcuts', True),
        }
        
        return context
```

## Performance Optimization Features

### 1. Virtual Scrolling

For large datasets:
```python
class ProductViewSet(JqGridConfigMixin, viewsets.ModelViewSet):
    # Enable virtual scrolling
    enable_virtual_scroll = True
    
    # Virtual scroll configuration
    virtual_scroll_config = {
        'rows_per_page': 50,
        'preload_pages': 2,
        'scroll_timeout': 200
    }
```

### 2. Lazy Loading

Load data on demand:
```python
class ProductViewSet(JqGridConfigMixin, viewsets.ModelViewSet):
    # Enable lazy loading
    enable_lazy_loading = True
    
    # Configure lazy loading
    lazy_load_config = {
        'initial_load': 100,
        'load_more_size': 50,
        'auto_load': True
    }
```

### 3. Column State Persistence

Save column preferences:
```python
class ProductViewSet(JqGridConfigMixin, viewsets.ModelViewSet):
    # Enable state persistence
    enable_state_persistence = True
    
    # What to persist
    persist_state = {
        'column_order': True,
        'column_widths': True,
        'sort_order': True,
        'filters': True,
        'page_size': True,
        'grouping': True
    }
```

## Template Tag Features

### Basic Grid
```django
{% load jqgrid_tags %}

{# Simple grid with default features #}
{% jqgrid "product_grid" "example" "product" %}

{# Grid with custom features #}
{% jqgrid "product_grid" "example" "product" 
    include_import_export=True 
    enable_grouping=True 
    enable_frozen_columns=True 
%}
```

### Custom Theme
```django
{# Use specific theme #}
{% jqgrid_theme 'bootstrap5' 'fontAwesome' %}

{# Use settings-based theme #}
{% jqgrid_theme %}

{# Custom CSS #}
{% jqgrid_theme theme='bootstrap4' custom_css='/static/css/custom-grid.css' %}
```

## Summary

Django jqGrid provides extensive features that can be enabled through:

1. **ViewSet mixins and properties** - Python-side configuration
2. **Settings.py** - Global defaults
3. **JavaScript configuration** - Client-side customization
4. **Template tags** - Per-grid options
5. **Dynamic methods** - Runtime feature control

Features can be mixed and matched based on requirements, with sensible defaults that work out of the box.