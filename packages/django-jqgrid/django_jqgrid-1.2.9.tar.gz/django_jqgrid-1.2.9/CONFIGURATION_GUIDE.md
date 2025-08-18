# Django jqGrid Configuration Guide

This guide provides detailed information about configuring django-jqgrid based on serializers and model metadata.

## Table of Contents

1. [Serializer-Based Configuration](#serializer-based-configuration)
2. [Field Type Mappings](#field-type-mappings)
3. [ViewSet Configuration](#viewset-configuration)
4. [Grid Options](#grid-options)
5. [Method Options](#method-options)
6. [Advanced Configuration](#advanced-configuration)

## Serializer-Based Configuration

The django-jqgrid package automatically generates grid configuration from your Django REST Framework serializers. This approach ensures consistency between your API and grid presentation.

### Basic Serializer Example

```python
from rest_framework import serializers
from .models import Product

class ProductSerializer(serializers.ModelSerializer):
    # Read-only fields automatically become non-editable in the grid
    total_revenue = serializers.ReadOnlyField()
    
    # Custom labels are used as column headers
    name = serializers.CharField(label="Product Name", max_length=200)
    
    # Field types determine grid column behavior
    price = serializers.DecimalField(
        max_digits=10, 
        decimal_places=2,
        label="Unit Price"
    )
    
    # Boolean fields become checkboxes
    in_stock = serializers.BooleanField(label="Available")
    
    # Date fields get date pickers
    created_at = serializers.DateTimeField(
        read_only=True,
        format="%Y-%m-%d %H:%M:%S"
    )
    
    # Related fields can be customized
    category_name = serializers.CharField(
        source='category.name',
        read_only=True,
        label="Category"
    )
    
    class Meta:
        model = Product
        fields = ['id', 'name', 'price', 'in_stock', 'category_name', 
                 'total_revenue', 'created_at']
```

### How Serializer Fields Map to Grid Columns

1. **Field Labels**: The `label` parameter becomes the column header
2. **Read-Only Fields**: Fields with `read_only=True` are not editable in the grid
3. **Required Fields**: Required fields are validated during grid editing
4. **Field Validation**: Serializer validators are applied during CRUD operations

## Field Type Mappings

The package automatically maps Django model field types to appropriate jqGrid column configurations:

### Text Fields

```python
# CharField
CharField → {
    'stype': 'text',
    'search_ops': ["eq", "ne", "cn", "nc", "bw", "bn", "ew", "en"],
    'searchoptions': {'sopt': [...]}
}

# TextField
TextField → {
    'stype': 'text',
    'edittype': 'textarea',
    'search_ops': ["eq", "ne", "cn", "nc", "bw", "bn", "ew", "en"]
}

# EmailField
EmailField → {
    'stype': 'email',
    'formatter': 'email',
    'search_ops': ["eq", "ne", "cn", "nc", "bw", "bn", "ew", "en"]
}

# URLField
URLField → {
    'stype': 'text',
    'formatter': 'link',
    'search_ops': ["eq", "ne", "cn", "nc", "bw", "bn", "ew", "en"]
}
```

### Numeric Fields

```python
# IntegerField
IntegerField → {
    'stype': 'integer',
    'align': 'right',
    'formatter': 'integer',
    'search_ops': ["eq", "ne", "lt", "le", "gt", "ge"]
}

# DecimalField
DecimalField → {
    'stype': 'number',
    'align': 'right',
    'formatter': 'number',
    'formatoptions': {'decimalPlaces': 2},  # from field definition
    'search_ops': ["eq", "ne", "lt", "le", "gt", "ge"]
}

# FloatField
FloatField → {
    'stype': 'number',
    'align': 'right',
    'formatter': 'number',
    'search_ops': ["eq", "ne", "lt", "le", "gt", "ge"]
}
```

### Date/Time Fields

```python
# DateField
DateField → {
    'stype': 'date',
    'align': 'center',
    'formatter': 'date',
    'formatoptions': {
        "srcformat": "ISO8601Short",
        "newformat": "Y-m-d"
    },
    'editoptions': {
        "dataInit": "initDatepicker",
        "datepicker": {"dateFormat": "yy-mm-dd"}
    },
    'search_ops': ["eq", "ne", "lt", "le", "gt", "ge"]
}

# DateTimeField
DateTimeField → {
    'stype': 'datetime-local',
    'align': 'center',
    'formatter': 'datetimeLocal',
    'edittype': 'datetime-local',
    'formatoptions': {
        "srcformat": "ISO8601",
        "newformat": "Y-m-d H:i:s"
    },
    'editoptions': {
        "dataInit": "initDatetimepicker",
        "datetimepicker": {
            "dateFormat": "yy-mm-dd",
            "timeFormat": "HH:mm:ss"
        }
    },
    'search_ops': ["eq", "ne", "lt", "le", "gt", "ge"]
}
```

### Boolean Fields

```python
BooleanField → {
    'stype': 'checkbox',
    'align': 'center',
    'formatter': 'checkbox',
    'edittype': 'checkbox',
    'editoptions': {"value": "1:0"},
    'search_ops': ["eq", "ne"]
}
```

### Relationship Fields

```python
# ForeignKey
ForeignKey → {
    'stype': 'select',
    'formatter': 'select',
    'edittype': 'select',
    'editoptions': {
        'dataUrl': '/api/{app}/{model}/dropdown/?field_name={field}',
        'dataType': 'application/json'
    },
    'search_ops': ["eq", "ne"]
}
```

### Special Fields

```python
# JSONField
JSONField → {
    'stype': 'textarea',
    'formatter': 'json',
    'edittype': 'textarea',
    'search_ops': ["eq", "ne", "cn", "nc"]
}

# ImageField
ImageField → {
    'stype': 'text',
    'formatter': 'image',
    'search_ops': ["eq", "ne", "cn", "nc", "bw", "bn", "ew", "en"]
}

# FileField
FileField → {
    'stype': 'text',
    'formatter': 'file',
    'search_ops': ["eq", "ne", "cn", "nc", "bw", "bn", "ew", "en"]
}
```

## ViewSet Configuration

The `JqGridConfigMixin` provides numerous configuration options:

### Basic Configuration

```python
from rest_framework import viewsets
from django_jqgrid.mixins import JqGridConfigMixin, JqGridBulkActionMixin

class ProductViewSet(JqGridConfigMixin, JqGridBulkActionMixin, viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    
    # Key field (defaults to 'id')
    key_field = 'id'
    
    # Visible columns in order
    visible_columns = ['id', 'name', 'price', 'category', 'in_stock', 'created_at']
    
    # Searchable fields
    search_fields = ['name', 'description', 'sku', 'category__name']
    
    # Sortable fields
    ordering_fields = ['name', 'price', 'created_at', 'category__name']
    
    # Default ordering (supports multiple fields)
    ordering = ['-created_at', 'name']
```

### Advanced Column Configuration

```python
class ProductViewSet(JqGridConfigMixin, viewsets.ModelViewSet):
    # ... basic configuration ...
    
    # Override specific field configurations
    jqgrid_field_overrides = {
        'price': {
            'formatter': 'currency',
            'formatoptions': {
                'prefix': '$',
                'suffix': ' USD',
                'thousandsSeparator': ',',
                'decimalPlaces': 2
            },
            'width': 120
        },
        'name': {
            'width': 300,
            'editoptions': {
                'size': 40,
                'maxlength': 200
            }
        },
        'description': {
            'edittype': 'textarea',
            'editoptions': {
                'rows': 5,
                'cols': 40
            },
            'hidden': True  # Hidden by default, can be shown via column chooser
        }
    }
    
    # Custom header titles (overrides model verbose_name)
    header_titles = {
        'sku': 'Product Code',
        'in_stock': 'Available',
        'created_at': 'Date Added'
    }
```

### Grouping Configuration

```python
class OrderViewSet(JqGridConfigMixin, viewsets.ModelViewSet):
    # ... basic configuration ...
    
    # Fields that can be grouped
    groupable_fields = ['status', 'customer', 'order_date']
    
    # Aggregation configuration
    aggregation_fields = {
        'total_amount': 'sum',
        'quantity': 'sum',
        'id': 'count'  # Count of orders
    }
    
    # Default grouping (optional)
    grouping_options = {
        'groupField': 'status',
        'groupColumnShow': [True],
        'groupText': ['<b>{0} - {1} Order(s)</b>'],
        'groupOrder': ['asc'],
        'groupSummary': [True],
        'showSummaryOnHide': True
    }
```

### Frozen Columns

```python
class CustomerViewSet(JqGridConfigMixin, viewsets.ModelViewSet):
    # ... basic configuration ...
    
    # Columns that stay visible when scrolling horizontally
    frozen_columns = ['id', 'name', 'email']
```

### Conditional Formatting

```python
class InventoryViewSet(JqGridConfigMixin, viewsets.ModelViewSet):
    # ... basic configuration ...
    
    # Apply conditional formatting to cells
    conditional_formatting = {
        'stock_level': {
            # Format based on value ranges
            'rules': [
                {
                    'condition': 'value < 10',
                    'style': {'color': 'red', 'fontWeight': 'bold'}
                },
                {
                    'condition': 'value >= 10 && value < 50',
                    'style': {'color': 'orange'}
                },
                {
                    'condition': 'value >= 50',
                    'style': {'color': 'green'}
                }
            ]
        },
        'status': {
            # Format based on exact values
            'active': {'color': 'green', 'background': '#e8f5e9'},
            'inactive': {'color': 'red', 'background': '#ffebee'},
            'pending': {'color': 'orange', 'background': '#fff3e0'}
        }
    }
    
    # Row highlighting rules
    highlight_rules = {
        'critical': {
            'condition': 'row.stock_level < 5',
            'class': 'bg-danger text-white'
        },
        'warning': {
            'condition': 'row.stock_level < 20',
            'class': 'bg-warning'
        }
    }
```

### Bulk Operations

```python
class ProductViewSet(JqGridConfigMixin, JqGridBulkActionMixin, viewsets.ModelViewSet):
    # ... basic configuration ...
    
    # Fields that can be bulk updated
    bulk_updateable_fields = ['price', 'category', 'in_stock', 'discount']
    
    # Custom bulk actions
    bulk_actions = [
        {
            'id': 'apply-discount',
            'label': 'Apply Discount',
            'icon': 'fa-percent',
            'class': 'btn-success',
            'fields': ['discount_percentage']  # Custom fields for this action
        },
        {
            'id': 'change-category',
            'label': 'Change Category',
            'icon': 'fa-folder',
            'class': 'btn-info'
        },
        {
            'id': 'bulk-delete',
            'label': 'Delete Selected',
            'icon': 'fa-trash',
            'class': 'btn-danger',
            'confirm': 'Are you sure you want to delete selected items?'
        }
    ]
    
    # Override bulk update behavior
    def process_bulk_update(self, objs, updates):
        if 'discount_percentage' in updates:
            # Custom logic for discount
            discount = updates.pop('discount_percentage')
            for obj in objs:
                obj.price = obj.price * (1 - discount / 100)
                obj.save()
        
        # Call parent method for remaining updates
        return super().process_bulk_update(objs, updates)
```

## Grid Options

### Default Grid Options

```python
JQGRID_DEFAULT_GRID_OPTIONS = {
    "datatype": "json",
    "mtype": "GET",
    "headertitles": True,
    "styleUI": "Bootstrap4",
    "iconSet": "fontAwesome",
    "responsive": True,
    "rowNum": 25,
    "rowList": [25, 50, 100, 500, 1000],
    "viewrecords": True,
    "gridview": True,
    "height": 400,
    "autowidth": True,
    "multiselect": True,
    "rownumbers": True,
    "altRows": True,
    "hoverrows": True,
    "sortable": True,
    "toolbar": [True, "both"],
    "forceFit": False,
    "autoresizeOnLoad": True,
    "footerrow": True,
    "userDataOnFooter": True,
    "toppager": True,
    "autoencode": True
}
```

### Override Grid Options

```python
class CustomViewSet(JqGridConfigMixin, viewsets.ModelViewSet):
    # ... other configuration ...
    
    jqgrid_options_override = {
        'caption': 'Custom Grid Title',
        'height': 600,
        'rowNum': 50,
        'rowList': [50, 100, 200, 500],
        'multiselect': False,  # Disable multi-selection
        'rownumbers': False,   # Hide row numbers
        'toolbar': [False, ''],  # Hide toolbar
        'viewrecords': True,
        'recordtext': 'Showing {0} - {1} of {2} records',
        'emptyrecords': 'No records found',
        'loadtext': 'Loading data...',
        'pgtext': 'Page {0} of {1}'
    }
```

## Method Options

### Navigation Grid (navGrid)

```python
method_options = {
    "navGrid": {
        "selector": "#jqGridPager",
        "options": {
            "edit": True,
            "add": True,
            "del": True,
            "search": True,
            "refresh": True,
            "view": True,
            "position": "left",
            "closeOnEscape": True,
            "cloneToTop": True
        },
        "editOptions": {
            "closeOnEscape": True,
            "editCaption": "Edit Record",
            "recreateForm": True,
            "closeAfterEdit": True,
            "modal": True,
            "width": 600,
            "height": "auto",
            "reloadAfterSubmit": True
        },
        "addOptions": {
            "closeOnEscape": True,
            "recreateForm": True,
            "closeAfterAdd": True,
            "modal": True,
            "width": 600,
            "height": "auto",
            "reloadAfterSubmit": True
        },
        "delOptions": {
            "msg": "Are you sure you want to delete this record?",
            "reloadAfterSubmit": True,
            "closeOnEscape": True,
            "modal": True
        },
        "searchOptions": {
            "closeOnEscape": True,
            "multipleSearch": True,
            "multipleGroup": True,
            "showQuery": True,
            "closeAfterSearch": True,
            "recreateFilter": True
        },
        "viewOptions": {
            "closeOnEscape": True,
            "width": 800,
            "modal": True
        }
    }
}
```

### Filter Toolbar

```python
method_options = {
    "filterToolbar": {
        "options": {
            "stringResult": True,
            "defaultSearch": "cn",  # Contains
            "searchOperators": True,
            "autosearch": True,
            "searchOnEnter": False,
            "beforeSearch": "function() { /* custom logic */ }",
            "afterSearch": "function() { /* custom logic */ }"
        }
    }
}
```

### Custom Navigation Buttons

```python
method_options = {
    "navButtonAdd": [
        {
            "selector": "#jqGridPager",
            "button": {
                "caption": "Export",
                "title": "Export Data",
                "buttonicon": "fa fa-download",
                "onClickButton": "handleExport",
                "position": "last"
            }
        },
        {
            "selector": "#jqGridPager",
            "button": {
                "caption": "Import",
                "title": "Import Data",
                "buttonicon": "fa fa-upload",
                "onClickButton": "handleImport",
                "position": "last"
            }
        },
        {
            "selector": "#jqGridPager",
            "button": {
                "caption": "Columns",
                "title": "Choose Columns",
                "buttonicon": "fa fa-columns",
                "onClickButton": "showColumnChooser",
                "position": "last"
            }
        }
    ]
}
```

## Advanced Configuration

### Import/Export Configuration

```python
class DataViewSet(JqGridConfigMixin, viewsets.ModelViewSet):
    # ... other configuration ...
    
    import_config = {
        'supported_formats': ['csv', 'xlsx', 'json'],
        'max_file_size': 10 * 1024 * 1024,  # 10MB
        'field_mapping': {
            # CSV/Excel column name → Model field name
            'Product Name': 'name',
            'Unit Price': 'price',
            'Stock': 'stock_level',
            'Category': 'category.name'
        },
        'validators': {
            'price': lambda x: float(x) > 0,
            'stock_level': lambda x: int(x) >= 0
        },
        'preprocessors': {
            'name': lambda x: x.strip().title(),
            'sku': lambda x: x.upper()
        }
    }
    
    export_config = {
        'formats': ['csv', 'xlsx', 'pdf', 'json'],
        'include_headers': True,
        'max_rows': 10000,
        'field_labels': {
            'name': 'Product Name',
            'price': 'Unit Price ($)',
            'stock_level': 'Current Stock'
        },
        'excluded_fields': ['internal_notes', 'created_by'],
        'datetime_format': '%Y-%m-%d %H:%M:%S'
    }
```

### Custom Filter Storage

```python
class CustomFilterViewSet(JqGridConfigMixin, viewsets.ModelViewSet):
    # ... other configuration ...
    
    def get_tmplgilters(self):
        """Override to customize filter template retrieval"""
        from django_jqgrid.models import GridFilter
        from django.contrib.contenttypes.models import ContentType
        
        # Get content type for this model
        ct = ContentType.objects.get_for_model(self.queryset.model)
        
        # Get user's private filters
        user_filters = GridFilter.objects.filter(
            table=ct,
            created_by=self.request.user,
            is_global=False
        )
        
        # Get shared team filters
        team_filters = GridFilter.objects.filter(
            table=ct,
            is_global=True,
            created_by__groups__in=self.request.user.groups.all()
        ).distinct()
        
        # Format for jqGrid
        filters_data = []
        for f in user_filters:
            filters_data.append({
                'id': f.id,
                'name': f.name,
                'value': f.value,
                'type': 'personal'
            })
        
        for f in team_filters:
            filters_data.append({
                'id': f.id,
                'name': f'{f.name} (Team)',
                'value': f.value,
                'type': 'team'
            })
        
        return {
            'tmplIds': [f['id'] for f in filters_data],
            'tmplNames': [f['name'] for f in filters_data],
            'tmplFilters': [f['value'] for f in filters_data]
        }
```

### Dynamic Configuration

```python
class DynamicViewSet(JqGridConfigMixin, viewsets.ModelViewSet):
    # ... other configuration ...
    
    def get_visible_columns(self):
        """Dynamically determine visible columns based on user permissions"""
        base_columns = ['id', 'name', 'status', 'created_at']
        
        if self.request.user.has_perm('app.view_financial_data'):
            base_columns.extend(['price', 'cost', 'profit_margin'])
        
        if self.request.user.has_perm('app.view_inventory'):
            base_columns.extend(['stock_level', 'reorder_point'])
        
        if self.request.user.is_superuser:
            base_columns.extend(['internal_notes', 'audit_log'])
        
        return base_columns
    
    def get_jqgrid_options_override(self):
        """Dynamic grid options based on context"""
        options = {}
        
        # Different heights for different screen sizes
        if self.request.GET.get('mobile') == 'true':
            options['height'] = 300
            options['rowNum'] = 10
        else:
            options['height'] = 600
            options['rowNum'] = 50
        
        return options
```

## Settings Configuration

You can define default configurations in your Django settings:

```python
# settings.py

# Default grid options applied to all grids
JQGRID_DEFAULT_GRID_OPTIONS = {
    'rowNum': 25,
    'rowList': [25, 50, 100, 500, 1000],
    'height': 400,
    'styleUI': 'Bootstrap4',
    'iconSet': 'fontAwesome',
    'responsive': True
}

# Default field type configurations
JQGRID_DEFAULT_FIELD_CONFIG = {
    'DateField': {
        'formatoptions': {"srcformat": "ISO8601Short", "newformat": "d/m/Y"}
    },
    'DecimalField': {
        'formatoptions': {"decimalPlaces": 2, "thousandsSeparator": ","}
    },
    'IntegerField': {
        'formatoptions': {"thousandsSeparator": ","}
    }
}

# Default method options
JQGRID_DEFAULT_METHOD_OPTIONS = {
    'navGrid': {
        'options': {
            'edit': True,
            'add': True,
            'del': True,
            'search': True,
            'refresh': True
        }
    },
    'filterToolbar': {
        'options': {
            'stringResult': True,
            'searchOperators': True
        }
    }
}

# Security settings
JQGRID_SECURITY = {
    'ENFORCE_PERMISSIONS': True,
    'AUDIT_CHANGES': True,
    'MAX_EXPORT_ROWS': 10000,
    'RATE_LIMIT': '100/hour'
}
```

## Best Practices

1. **Use Serializers**: Let serializers define field behavior and validation
2. **Override Sparingly**: Only override when necessary, rely on defaults
3. **Security First**: Always validate permissions in ViewSets
4. **Performance**: Use select_related() and prefetch_related() in querysets
5. **Consistency**: Maintain consistent naming between models, serializers, and grids

## Troubleshooting

### Common Issues

1. **Columns not showing**: Check `visible_columns` includes the field
2. **Search not working**: Ensure field is in `search_fields`
3. **Sort not working**: Add field to `ordering_fields`
4. **Foreign keys not loading**: Verify dropdown URL is accessible
5. **Date formatting issues**: Check date format in serializer and grid options

### Debug Mode

Enable debug logging to troubleshoot configuration issues:

```python
import logging

logger = logging.getLogger('django_jqgrid')
logger.setLevel(logging.DEBUG)

class DebugViewSet(JqGridConfigMixin, viewsets.ModelViewSet):
    # ... configuration ...
    
    def initgrid(self):
        super().initgrid()
        logger.debug(f"Grid config: {self.jqgrid_options}")
        logger.debug(f"Column model: {self.colmodel}")
```

## Feature Flags and Settings

### Global Feature Configuration

Configure features globally in your Django settings:

```python
# settings.py

# Basic jqGrid settings
JQGRID_DEFAULT_ROWS = 25
JQGRID_MAX_ROWS = 1000

# Theme configuration
JQGRID_THEME = 'bootstrap4'  # Options: 'bootstrap', 'bootstrap4', 'bootstrap5', 'jqueryui'
JQGRID_ICON_SET = 'fontAwesome'  # Options: 'fontAwesome', 'bootstrap', 'jQueryUI', 'glyph'
JQGRID_CUSTOM_CSS = None  # Path to custom CSS file

# Feature flags
JQGRID_FEATURES = {
    # Core features
    'ENABLE_SORTING': True,
    'ENABLE_SEARCHING': True,
    'ENABLE_PAGINATION': True,
    'ENABLE_COLUMN_REORDERING': True,
    'ENABLE_COLUMN_RESIZING': True,
    
    # Advanced features
    'ENABLE_BULK_OPERATIONS': True,
    'ENABLE_INLINE_EDITING': True,
    'ENABLE_CELL_EDITING': False,
    'ENABLE_GROUPING': True,
    'ENABLE_FROZEN_COLUMNS': True,
    'ENABLE_SUBGRID': True,
    'ENABLE_TREE_GRID': True,
    
    # Import/Export features
    'ENABLE_EXPORT': True,
    'ENABLE_IMPORT': True,
    'EXPORT_FORMATS': ['excel', 'csv', 'pdf'],
    'IMPORT_FORMATS': ['excel', 'csv'],
    
    # UI features
    'ENABLE_COLUMN_CHOOSER': True,
    'ENABLE_FILTER_TOOLBAR': True,
    'ENABLE_FILTER_SAVE': True,
    'ENABLE_THEMES': True,
    'ENABLE_RESPONSIVE_MODE': True,
    'ENABLE_TOOLTIPS': True,
    'ENABLE_CONTEXT_MENU': True,
    
    # Performance features
    'ENABLE_VIRTUAL_SCROLL': False,
    'ENABLE_LAZY_LOADING': False,
    'ENABLE_STATE_PERSISTENCE': True,
    'ENABLE_CACHING': True,
    'CACHE_TIMEOUT': 300,  # seconds
}

# Performance optimization
JQGRID_OPTIMIZATION = {
    'USE_SELECT2': True,  # Enhanced dropdowns
    'DEBOUNCE_SEARCH': 300,  # milliseconds
    'MIN_SEARCH_LENGTH': 2,
    'BATCH_SIZE': 100,
    'VIRTUAL_SCROLL_THRESHOLD': 1000,
}

# Security settings
JQGRID_SECURITY = {
    'REQUIRE_CSRF': True,
    'VALIDATE_PERMISSIONS': True,
    'LOG_BULK_OPERATIONS': True,
    'MAX_EXPORT_ROWS': 10000,
}
```

### ViewSet-Level Feature Control

Override global settings for specific ViewSets:

```python
class ProductViewSet(JqGridConfigMixin, viewsets.ModelViewSet):
    # Enable/disable features for this ViewSet
    jqgrid_features = {
        'enable_bulk_operations': True,
        'enable_inline_editing': False,  # Override global setting
        'enable_export': True,
        'enable_import': False,
        'enable_grouping': True,
        'enable_filter_save': True,
    }
    
    # Feature-specific configuration
    bulk_updateable_fields = ['price', 'category', 'status']
    groupable_fields = ['category', 'status']
    export_formats = ['excel', 'csv']  # Limit export formats
    
    def get_jqgrid_features(self):
        """Dynamically determine features based on user permissions."""
        features = super().get_jqgrid_features()
        
        # Disable editing for non-staff users
        if not self.request.user.is_staff:
            features['enable_inline_editing'] = False
            features['enable_bulk_operations'] = False
            
        # Enable import only for superusers
        if self.request.user.is_superuser:
            features['enable_import'] = True
            
        return features
```

### JavaScript Feature Configuration

Configure features on the client side:

```javascript
// Global feature configuration
window.jqGridConfig.features = {
    // UI features
    enableTooltips: true,
    enableKeyboardNavigation: true,
    enableContextMenu: true,
    enableDragAndDrop: false,
    
    // Performance features
    enableAutoSave: false,
    autoSaveInterval: 30000,  // milliseconds
    enableBatchMode: true,
    
    // Behavior features
    confirmDelete: true,
    confirmBulkOperations: true,
    showLoadingOverlay: true,
    enableShortcuts: true
};

// Per-grid feature override
window.initializeTableInstance('productGrid', 'example', 'product', {
    features: {
        enableGrouping: true,
        enableFrozenColumns: true,
        enableColumnReordering: true,
        enableAutoSave: true
    }
});
```

### Feature Dependencies

Some features require other features to be enabled:

```python
# Cell editing requires inline editing
if JQGRID_FEATURES['ENABLE_CELL_EDITING']:
    JQGRID_FEATURES['ENABLE_INLINE_EDITING'] = True

# Import requires bulk operations
if JQGRID_FEATURES['ENABLE_IMPORT']:
    JQGRID_FEATURES['ENABLE_BULK_OPERATIONS'] = True

# Filter save requires filter toolbar
if JQGRID_FEATURES['ENABLE_FILTER_SAVE']:
    JQGRID_FEATURES['ENABLE_FILTER_TOOLBAR'] = True
```

### Conditional Feature Loading

Load features based on conditions:

```python
class ConditionalViewSet(JqGridConfigMixin, viewsets.ModelViewSet):
    def initgrid(self):
        super().initgrid()
        
        # Enable features based on data size
        count = self.get_queryset().count()
        if count > 1000:
            self.jqgrid_features['enable_virtual_scroll'] = True
            self.jqgrid_features['enable_lazy_loading'] = True
            
        # Enable features based on model
        if hasattr(self.model, 'parent'):
            self.jqgrid_features['enable_tree_grid'] = True
            
        # Enable features based on time
        import datetime
        if datetime.datetime.now().hour >= 9 and datetime.datetime.now().hour <= 17:
            self.jqgrid_features['enable_realtime_updates'] = True
```

### Feature-Specific Settings

Each feature can have its own configuration:

```python
# Grouping feature settings
JQGRID_GROUPING_CONFIG = {
    'groupCollapse': False,
    'groupSummary': True,
    'showSummaryOnHide': True,
    'groupDataSorted': True,
}

# Export feature settings
JQGRID_EXPORT_CONFIG = {
    'excel': {
        'include_headers': True,
        'freeze_headers': True,
        'auto_fit_columns': True,
        'include_filters': True,
    },
    'csv': {
        'delimiter': ',',
        'include_headers': True,
        'encoding': 'utf-8',
    },
    'pdf': {
        'orientation': 'landscape',
        'page_size': 'A4',
        'include_logo': True,
    }
}

# Import feature settings
JQGRID_IMPORT_CONFIG = {
    'preview_rows': 10,
    'batch_size': 100,
    'update_existing': True,
    'skip_errors': False,
    'validation_strict': True,
}
```

### Checking Features in Templates

Use template tags to conditionally show features:

```django
{% load jqgrid_tags %}

{% if features.enable_import %}
    <button id="importBtn" class="btn btn-success">
        <i class="fa fa-upload"></i> Import Data
    </button>
{% endif %}

{% if features.enable_export %}
    <div class="dropdown">
        <button class="btn btn-primary dropdown-toggle">Export</button>
        <div class="dropdown-menu">
            {% for format in export_formats %}
                <a class="dropdown-item" href="#" data-format="{{ format }}">
                    Export as {{ format|upper }}
                </a>
            {% endfor %}
        </div>
    </div>
{% endif %}
```

## Feature Reference

For a complete list of all features and their configuration options, see the [Features Guide](FEATURES_GUIDE.md).