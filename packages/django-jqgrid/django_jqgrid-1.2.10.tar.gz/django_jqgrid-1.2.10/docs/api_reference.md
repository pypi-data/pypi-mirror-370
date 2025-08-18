# Django jqGrid API Reference

## Table of Contents

1. [Mixins](#mixins)
2. [ViewSet Methods](#viewset-methods)
3. [API Endpoints](#api-endpoints)
4. [JavaScript Functions](#javascript-functions)
5. [Models](#models)
6. [Serializers](#serializers)
7. [Settings](#settings)
8. [Utility Functions](#utility-functions)

## Mixins

### JqGridConfigMixin

The main mixin that provides jqGrid configuration capabilities to Django REST Framework ViewSets.

```python
from django_jqgrid.mixins import JqGridConfigMixin

class YourViewSet(JqGridConfigMixin, viewsets.ModelViewSet):
    # Your configuration here
```

#### Properties

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `key_field` | str | 'id' | Primary key field name |
| `visible_columns` | list | All serializer fields | Columns to display in grid |
| `search_fields` | list | All serializer fields | Searchable fields |
| `ordering_fields` | list | All serializer fields | Sortable fields |
| `ordering` | list/str | None | Default sort order |
| `groupable_fields` | list | [] | Fields available for grouping |
| `frozen_columns` | list | [] | Columns that stay visible when scrolling |
| `header_titles` | dict | {} | Custom column headers |
| `jqgrid_field_overrides` | dict | {} | Field-specific configuration overrides |
| `jqgrid_options_override` | dict | {} | Grid options overrides |
| `conditional_formatting` | dict | {} | Cell formatting rules |
| `highlight_rules` | dict | {} | Row highlighting rules |
| `additional_data` | dict | {} | Extra data to include in config response |

#### Methods

##### `initgrid()`

Initializes the grid configuration. Called automatically by `jqgrid_config` endpoint.

```python
def initgrid(self):
    """Initialize the grid configuration"""
    # Sets up:
    # - self.colmodel: Column definitions
    # - self.colnames: Column headers
    # - self.jqgrid_options: Grid options
    # - self.method_options: Method configurations
```

##### `initialize_columns()`

Builds column model from serializer fields.

```python
def initialize_columns(self):
    """Initialize column model from serializer fields"""
    # Processes each field in visible_columns
    # Applies field type configurations
    # Sets up search and edit options
```

##### `configure_grid_options()`

Configures main jqGrid options.

```python
def configure_grid_options(self):
    """Configure jqGrid main options"""
    # Sets URL, caption, sorting, etc.
    # Applies DEFAULT_GRID_OPTIONS
    # Applies jqgrid_options_override
```

##### `configure_method_options()`

Configures jqGrid method options (navGrid, filterToolbar, etc.).

```python
def configure_method_options(self):
    """Configure method options for jqGrid"""
    # Sets up navigation grid
    # Configures filter toolbar
    # Applies method_options_override
```

##### `get_tmplgilters()`

Retrieves saved filter templates.

```python
def get_tmplgilters(self):
    """Get template filters for search options"""
    # Returns: {
    #     'tmplNames': [...],
    #     'tmplFilters': [...],
    #     'tmplIds': [...]
    # }
```

##### `generate_filter_mappings()`

Generates Django ORM filter mappings for jqGrid search operators.

```python
def generate_filter_mappings(self):
    """Generate filter mappings for jqGrid search toolbox"""
    # Returns: {
    #     'field__jq_eq': 'field',
    #     'field__jq_ne': 'field__ne',
    #     'field__jq_lt': 'field__lt',
    #     # ... etc
    # }
```

### JqGridBulkActionMixin

Provides bulk update and delete functionality.

```python
from django_jqgrid.mixins import JqGridBulkActionMixin

class YourViewSet(JqGridBulkActionMixin, viewsets.ModelViewSet):
    allowed_bulk_fields = ['status', 'category']
```

#### Properties

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `allowed_bulk_fields` | list | [] | Fields that can be bulk updated |
| `bulk_updateable_fields` | list | Auto-generated | Fields available for bulk update |
| `bulk_actions` | list | Default actions | Available bulk actions |

#### Methods

##### `get_bulk_queryset(ids)`

Returns queryset filtered by provided IDs.

```python
def get_bulk_queryset(self, ids):
    """Return queryset filtered by IDs"""
    # Parameters:
    #   ids: List of primary key values
    # Returns: QuerySet
```

##### `get_bulk_editable_fields()`

Returns list of fields that can be bulk edited.

```python
def get_bulk_editable_fields(self):
    """Get allowed fields for bulk update"""
    # Returns: List of field names
```

##### `validate_bulk_data(data)`

Validates bulk action request data.

```python
def validate_bulk_data(self, data):
    """Validate bulk request data"""
    # Parameters:
    #   data: Request data dict
    # Returns: (ids, action_data) tuple
    # Raises: ValidationError
```

##### `process_bulk_update(objs, updates)`

Processes bulk update operation.

```python
def process_bulk_update(self, objs, updates):
    """Process bulk update"""
    # Parameters:
    #   objs: QuerySet of objects to update
    #   updates: Dict of field: value pairs
    # Returns: Result dict
```

## ViewSet Methods

### Action Decorators

#### `@action` jqgrid_config

Returns jqGrid configuration.

```python
@action(methods=['get'], detail=False)
def jqgrid_config(self, request, *args, **kwargs):
    """Return jqGrid configuration"""
    # GET /api/app/model/jqgrid_config/
    # Returns: {
    #     'jqgrid_options': {...},
    #     'method_options': {...},
    #     'bulk_action_config': {...},
    #     'header_titles': {...},
    #     # Additional data
    # }
```

#### `@action` crud

Handles jqGrid CRUD operations.

```python
@action(methods=['post'], detail=False, url_path='crud')
def crud(self, request, *args, **kwargs):
    """Handle CRUD operations via jqGrid"""
    # POST /api/app/model/crud/
    # Request data:
    #   oper: 'add' | 'edit' | 'del'
    #   id: Record ID (for edit/del)
    #   field_name: value (for add/edit)
```

#### `@action` bulk_action

Handles bulk operations.

```python
@action(methods=['post'], detail=False)
def bulk_action(self, request):
    """Handle bulk update/delete"""
    # POST /api/app/model/bulk_action/
    # Request data:
    # {
    #     "ids": [1, 2, 3],
    #     "action": {
    #         "field": "value",
    #         // or
    #         "_delete": true
    #     }
    # }
```

## API Endpoints

### Grid Configuration

#### GET `/api/<app>/<model>/jqgrid_config/`

Returns complete jqGrid configuration.

**Response:**
```json
{
    "jqgrid_options": {
        "url": "/api/app/model/",
        "editurl": "/api/app/model/crud/",
        "colModel": [...],
        "colNames": [...],
        "sortname": "id",
        "sortorder": "asc",
        // ... other options
    },
    "method_options": {
        "navGrid": {...},
        "filterToolbar": {...}
    },
    "bulk_action_config": {
        "actions": [...],
        "updateableFields": [...]
    },
    "header_titles": {...},
    "import_config": {...},
    "export_config": {...}
}
```

### Data Operations

#### GET `/api/<app>/<model>/`

Lists records with jqGrid parameters.

**Query Parameters:**
- `page`: Page number (default: 1)
- `page_size` or `rows`: Records per page
- `sidx`: Sort field
- `sord`: Sort order ('asc' or 'desc')
- `_search`: Enable search (true/false)
- `filters`: JSON search filters
- Field-specific filters

**Response:**
```json
{
    "data": {
        "page": 1,
        "total_pages": 10,
        "records": 100,
        "data": [
            {"id": 1, "name": "Product 1", ...},
            {"id": 2, "name": "Product 2", ...}
        ]
    }
}
```

#### POST `/api/<app>/<model>/crud/`

Handles CRUD operations from jqGrid.

**Add Operation:**
```json
{
    "oper": "add",
    "name": "New Product",
    "price": 29.99,
    "category": 1
}
```

**Edit Operation:**
```json
{
    "oper": "edit",
    "id": 1,
    "name": "Updated Product",
    "price": 39.99
}
```

**Delete Operation:**
```json
{
    "oper": "del",
    "id": 1
}
```

#### POST `/api/<app>/<model>/bulk_action/`

Handles bulk operations.

**Bulk Update:**
```json
{
    "ids": [1, 2, 3],
    "action": {
        "category": 5,
        "in_stock": true
    }
}
```

**Bulk Delete:**
```json
{
    "ids": [1, 2, 3],
    "action": {
        "_delete": true
    }
}
```

**Response:**
```json
{
    "status": "success",
    "message": "Updated 3 records",
    "updated_ids": [1, 2, 3]
}
```

### Dropdown Data

#### GET `/api/<app>/<model>/dropdown/`

Returns data for select dropdowns.

**Query Parameters:**
- `field_name`: Field requesting dropdown for
- `format`: Response format (json)
- `all`: Include all options (true/false)

**Response:**
```json
{
    "": "All",
    "1": "Category 1",
    "2": "Category 2"
}
```

## JavaScript Functions

### Grid Initialization

```javascript
// Initialize jqGrid with API configuration
function initializeGrid(gridId, apiUrl) {
    $.getJSON(apiUrl + 'jqgrid_config/', function(config) {
        $('#' + gridId).jqGrid(config.jqgrid_options);
        
        // Apply navigation grid
        $('#' + gridId).jqGrid('navGrid', '#' + gridId + 'Pager',
            config.method_options.navGrid.options,
            config.method_options.navGrid.editOptions,
            config.method_options.navGrid.addOptions,
            config.method_options.navGrid.delOptions,
            config.method_options.navGrid.searchOptions,
            config.method_options.navGrid.viewOptions
        );
        
        // Apply filter toolbar
        $('#' + gridId).jqGrid('filterToolbar', 
            config.method_options.filterToolbar.options
        );
    });
}
```

### Form Response Handlers

```javascript
// Handle form submission responses
window.handleFormResponse = function(response, postdata) {
    if (response.responseJSON) {
        if (response.responseJSON.success === false) {
            return [false, response.responseJSON.message || 'Error occurred'];
        }
    }
    return [true, '', ''];
};

// Handle submission errors
window.handleSubmitError = function(response) {
    if (response.responseJSON && response.responseJSON.message) {
        return response.responseJSON.message;
    }
    return 'An error occurred while processing your request';
};
```

### Export/Import Handlers

```javascript
// Handle data export
window.handleExport = function() {
    var gridId = $(this).data('gridId') || 'jqGrid';
    var postData = $('#' + gridId).jqGrid('getGridParam', 'postData');
    
    // Build export URL with current filters
    var exportUrl = $('#' + gridId).jqGrid('getGridParam', 'url') + 'export/';
    exportUrl += '?' + $.param(postData);
    
    window.location.href = exportUrl;
};

// Handle data import
window.handleImport = function() {
    // Show import dialog
    $('#importDialog').modal('show');
};
```

### Bulk Action Handlers

```javascript
// Execute bulk action
function executeBulkAction(gridId, actionId) {
    var selectedIds = $('#' + gridId).jqGrid('getGridParam', 'selarrrow');
    
    if (selectedIds.length === 0) {
        alert('Please select at least one record');
        return;
    }
    
    var actionData = {};
    if (actionId === 'bulk-delete') {
        actionData._delete = true;
    } else {
        // Collect field values from form
        $('#bulkUpdateForm').serializeArray().forEach(function(field) {
            actionData[field.name] = field.value;
        });
    }
    
    $.ajax({
        url: $('#' + gridId).jqGrid('getGridParam', 'url') + 'bulk_action/',
        method: 'POST',
        data: JSON.stringify({
            ids: selectedIds,
            action: actionData
        }),
        contentType: 'application/json',
        success: function(response) {
            $('#' + gridId).trigger('reloadGrid');
            alert(response.message);
        },
        error: function(xhr) {
            alert('Error: ' + xhr.responseJSON.message);
        }
    });
}
```

## Models

### GridFilter

Stores user-defined grid filters.

```python
from django_jqgrid.models import GridFilter

class GridFilter(models.Model):
    name = models.CharField(max_length=255)
    key = models.CharField(max_length=50)
    value = models.TextField()
    table = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    is_global = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

#### Fields

| Field | Type | Description |
|-------|------|-------------|
| `name` | CharField | Display name of the filter |
| `key` | CharField | Filter type (e.g., 'tmplFilters') |
| `value` | TextField | JSON-encoded filter data |
| `table` | ForeignKey | Content type of filtered model |
| `created_by` | ForeignKey | User who created the filter |
| `is_global` | BooleanField | Whether filter is shared |
| `created_at` | DateTimeField | Creation timestamp |
| `updated_at` | DateTimeField | Last update timestamp |

## Serializers

### GridFilterSerializer

Serializes GridFilter model with nested relationships.

```python
from django_jqgrid.serializers import GridFilterSerializer

class GridFilterSerializer(serializers.ModelSerializer):
    table_details = ContentTypeSerializer(source='table', read_only=True)
    created_by_details = UserSerializer(source='created_by', read_only=True)
    
    class Meta:
        model = GridFilter
        fields = [
            'id', 'name', 'key', 'value', 'table', 'table_details',
            'created_by', 'created_by_details', 'is_global',
            'created_at', 'updated_at'
        ]
```

## Settings

### Configuration Settings

```python
# Default grid options
JQGRID_DEFAULT_GRID_OPTIONS = {
    'rowNum': 25,
    'rowList': [25, 50, 100, 500, 1000],
    'height': 400,
    'styleUI': 'Bootstrap4',
    'iconSet': 'fontAwesome',
    # ... other options
}

# Field type configurations
JQGRID_DEFAULT_FIELD_CONFIG = {
    'CharField': {
        'stype': 'text',
        'search_ops': ["eq", "ne", "cn", "nc", "bw", "bn", "ew", "en"]
    },
    # ... other field types
}

# Method options
JQGRID_DEFAULT_METHOD_OPTIONS = {
    'navGrid': {
        'options': {...},
        'editOptions': {...},
        # ... other options
    }
}
```

### Security Settings

```python
# Security configuration
JQGRID_SECURITY = {
    'ENFORCE_PERMISSIONS': True,  # Check model permissions
    'AUDIT_CHANGES': True,       # Log CRUD operations
    'MAX_EXPORT_ROWS': 10000,    # Export limit
    'RATE_LIMIT': '100/hour'     # API rate limiting
}
```

### Performance Settings

```python
# Performance tuning
JQGRID_PERFORMANCE = {
    'ENABLE_CACHING': True,
    'CACHE_TIMEOUT': 300,  # 5 minutes
    'DEFAULT_PAGE_SIZE': 25,
    'MAX_PAGE_SIZE': 1000
}
```

## Error Codes

| Code | Description |
|------|-------------|
| 400 | Bad Request - Invalid parameters |
| 401 | Unauthorized - Authentication required |
| 403 | Forbidden - Permission denied |
| 404 | Not Found - Resource doesn't exist |
| 422 | Unprocessable Entity - Validation error |
| 500 | Internal Server Error |

### Error Response Format

```json
{
    "status": "error",
    "message": "Human-readable error message",
    "errors": {
        "field_name": ["Error message 1", "Error message 2"]
    },
    "code": "ERROR_CODE"
}
```

## Examples

### Complete ViewSet Example

```python
from rest_framework import viewsets
from django_jqgrid.mixins import JqGridConfigMixin, JqGridBulkActionMixin
from .models import Product
from .serializers import ProductSerializer

class ProductViewSet(JqGridConfigMixin, JqGridBulkActionMixin, viewsets.ModelViewSet):
    queryset = Product.objects.select_related('category').all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    # Grid configuration
    visible_columns = ['id', 'name', 'price', 'category', 'in_stock']
    search_fields = ['name', 'description', 'category__name']
    ordering_fields = ['name', 'price', 'created_at']
    ordering = ['-created_at']
    
    # Advanced features
    groupable_fields = ['category']
    frozen_columns = ['id', 'name']
    bulk_updateable_fields = ['price', 'category', 'in_stock']
    
    # Field customization
    jqgrid_field_overrides = {
        'price': {
            'formatter': 'currency',
            'formatoptions': {'prefix': '$'}
        }
    }
    
    # Conditional formatting
    conditional_formatting = {
        'in_stock': {
            'false': {'color': 'red'},
            'true': {'color': 'green'}
        }
    }
    
    def get_queryset(self):
        """Apply custom filtering"""
        qs = super().get_queryset()
        # Add custom logic here
        return qs
```

## Utility Functions

### get_content_type_cached

Get ContentType with caching to reduce database queries.

```python
from django_jqgrid.utils import get_content_type_cached

content_type = get_content_type_cached('myapp', 'mymodel', cache_timeout=3600)
```

**Parameters:**
- `app_label` (str): Django app label
- `model_name` (str): Model name
- `cache_timeout` (int): Cache timeout in seconds (default: 3600)

**Returns:** ContentType instance or None

### parse_jqgrid_filters

Parse jqGrid filter string into Django ORM lookup format.

```python
from django_jqgrid.utils import parse_jqgrid_filters

filters = parse_jqgrid_filters(request.GET.get('filters'))
queryset = MyModel.objects.filter(**filters['filter']).exclude(**filters['exclude'])
```

**Parameters:**
- `filters_str` (str): JSON string containing jqGrid filters

**Returns:** Dictionary with 'filter' and 'exclude' keys

### get_model_field_info

Get detailed information about a model field.

```python
from django_jqgrid.utils import get_model_field_info

field_info = get_model_field_info(MyModel, 'field_name')
```

**Parameters:**
- `model`: Django model class
- `field_name` (str): Field name

**Returns:** Dictionary with field information

### format_value_for_export

Format a value for export (CSV, Excel, etc.).

```python
from django_jqgrid.utils import format_value_for_export

formatted = format_value_for_export(value, field_type='DateField')
```

**Parameters:**
- `value`: The value to format
- `field_type` (str): Optional field type for specific formatting

**Returns:** Formatted value as string

### get_jqgrid_sort_params

Extract and parse jqGrid sorting parameters from request.

```python
from django_jqgrid.utils import get_jqgrid_sort_params

ordering = get_jqgrid_sort_params(request)
queryset = MyModel.objects.order_by(*ordering)
```

**Parameters:**
- `request`: Django request object

**Returns:** List of ordering fields for Django ORM

### build_jqgrid_response

Build a properly formatted jqGrid response.

```python
from django_jqgrid.utils import build_jqgrid_response

response_data = build_jqgrid_response(
    queryset=page_objects,
    page=1,
    page_size=25,
    total_count=100
)
```

**Parameters:**
- `queryset`: The queryset or list of objects
- `page` (int): Current page number
- `page_size` (int): Number of items per page
- `total_count` (int): Optional total count

**Returns:** Dictionary formatted for jqGrid