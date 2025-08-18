# Django jqGrid Quick API Reference

## ViewSet Configuration

### JqGridConfigMixin Attributes

```python
class MyViewSet(JqGridConfigMixin, viewsets.ModelViewSet):
    # Column visibility
    visible_columns = ['id', 'name', 'price']  # List of visible columns
    
    # Search configuration
    search_fields = ['name', 'description']  # Fields available for searching
    
    # Sorting configuration
    ordering_fields = ['name', 'price', 'created_at']  # Sortable fields
    ordering = ['-created_at']  # Default ordering
    
    # Grouping configuration
    groupable_fields = ['category', 'status']  # Fields that can be grouped
    aggregation_fields = {  # Aggregation functions for grouped data
        'price': ['min', 'max', 'avg'],
        'quantity': ['sum']
    }
    
    # Frozen columns
    frozen_columns = ['id', 'name']  # Columns that stay fixed when scrolling
    
    # Field overrides
    jqgrid_field_overrides = {
        'price': {
            'formatter': 'currency',
            'align': 'right',
            'width': 100
        }
    }
    
    # Grid options override
    jqgrid_options_override = {
        'height': 600,
        'rowNum': 50
    }
    
    # Method options override
    method_options_override = {
        'navGrid': {
            'options': {'add': True, 'edit': True}
        }
    }
    
    # Conditional formatting
    conditional_formatting = {
        'quantity': [{
            'operator': 'lt',
            'value': 5,
            'backgroundColor': '#ffcccc'
        }]
    }
    
    # Row highlighting
    highlight_rules = [{
        'field': 'status',
        'operator': 'eq',
        'value': 'inactive',
        'cssClass': 'inactive-row'
    }]
```

### JqGridBulkActionMixin Attributes

```python
class MyViewSet(JqGridBulkActionMixin, viewsets.ModelViewSet):
    # Bulk updateable fields
    bulk_updateable_fields = ['status', 'category', 'price']
    
    # Custom bulk actions
    bulk_actions = [
        {
            'id': 'custom-action',
            'label': 'Custom Action',
            'icon': 'fa-star',
            'class': 'btn-warning'
        }
    ]
```

## JavaScript API

### Grid Initialization

```javascript
// Initialize a grid
window.initializeTableInstance(tableId, appName, tableName, options);

// Options object
{
    pagerSelector: '#customPager',
    onInitComplete: function(tableInstance) {},
    onGridComplete: function(tableInstance) {},
    onSelectRow: function(rowid, status, e, tableInstance) {},
    customButtons: [{
        id: 'custom-btn',
        label: 'Custom',
        icon: 'fa-star',
        class: 'btn-info',
        action: function(tableInstance) {}
    }]
}
```

### Table Instance Methods

```javascript
// Get table instance
const tableInstance = window.tables['myGridId'];

// Refresh grid
tableInstance.$grid.trigger('reloadGrid');

// Get selected rows
const selectedIds = tableInstance.$grid.jqGrid('getGridParam', 'selarrrow');

// Get row data
const rowData = tableInstance.$grid.jqGrid('getRowData', rowId);

// Update row
tableInstance.$grid.jqGrid('setRowData', rowId, newData);

// Delete row
tableInstance.$grid.jqGrid('delRowData', rowId);

// Show/hide columns
tableInstance.$grid.jqGrid('showCol', 'columnName');
tableInstance.$grid.jqGrid('hideCol', 'columnName');
```

### Global Configuration

```javascript
// Custom notification handler
window.jqGridConfig.notify = function(type, message, tableInstance) {
    // type: 'success', 'error', 'warning', 'info'
    return true; // Return false to use default
};

// Custom time formatter
window.jqGridConfig.timeSince = function(date) {
    return 'formatted time string';
};

// Register custom formatters
window.jqGridConfig.formatters.myFormatter = function(cellval, opts) {
    return `<span>${cellval}</span>`;
};

// Register custom buttons for table type
window.jqGridConfig.customButtons.product = [{
    id: 'import',
    label: 'Import',
    icon: 'fa-upload',
    class: 'btn-success',
    action: function(tableInstance) {}
}];
```

## REST API Endpoints

### Grid Configuration
```
GET /api/{app_name}/{model_name}/jqgrid_config/
```
Returns jqGrid configuration for the model.

### Data Operations
```
GET /api/{app_name}/{model_name}/
POST /api/{app_name}/{model_name}/
GET /api/{app_name}/{model_name}/{id}/
PUT /api/{app_name}/{model_name}/{id}/
DELETE /api/{app_name}/{model_name}/{id}/
```

### Bulk Operations
```
POST /api/{app_name}/{model_name}/bulk_action/
```
Body:
```json
{
    "ids": [1, 2, 3],
    "action": {
        "field1": "value1",
        "field2": "value2",
        "_delete": true  // For bulk delete
    }
}
```

### Grid Filters
```
GET /api/django_jqgrid/grid-filter/
POST /api/django_jqgrid/grid-filter/
DELETE /api/django_jqgrid/grid-filter/{id}/
```

## Template Tags

```django
{% load jqgrid_tags %}

<!-- Load CSS -->
{% jqgrid_css %}

<!-- Load dependencies (jQuery, etc.) -->
{% jqgrid_dependencies %}

<!-- Load jqGrid JavaScript -->
{% jqgrid_js %}

<!-- Render a grid -->
{% jqgrid "gridId" "app_name" "model_name" "Grid Title" %}
```

## Common Field Formatters

| Formatter | Description | Options |
|-----------|-------------|---------|
| `text` | Plain text (default) | - |
| `integer` | Integer numbers | - |
| `number` | Decimal numbers | `decimalPlaces` |
| `currency` | Currency format | `prefix`, `suffix`, `decimalPlaces` |
| `date` | Date format | `srcformat`, `newformat` |
| `checkbox` | Checkbox | - |
| `select` | Dropdown | `value` (choices) |
| `link` | Hyperlink | `target` |
| `email` | Email link | - |
| `image` | Image preview | - |
| `actions` | Action buttons | - |

## Search Operators

| Operator | Description | Applies To |
|----------|-------------|------------|
| `eq` | Equal | All types |
| `ne` | Not equal | All types |
| `lt` | Less than | Numbers, dates |
| `le` | Less or equal | Numbers, dates |
| `gt` | Greater than | Numbers, dates |
| `ge` | Greater or equal | Numbers, dates |
| `cn` | Contains | Text |
| `nc` | Not contains | Text |
| `bw` | Begins with | Text |
| `bn` | Not begins with | Text |
| `ew` | Ends with | Text |
| `en` | Not ends with | Text |
| `in` | In | All types |
| `ni` | Not in | All types |
| `nu` | Is null | All types |
| `nn` | Not null | All types |

## CSS Classes

### Grid Structure
- `.ui-jqgrid` - Main grid container
- `.ui-jqgrid-htable` - Header table
- `.ui-jqgrid-btable` - Body table
- `.ui-jqgrid-pager` - Pager container
- `.ui-jqgrid-toppager` - Top pager

### Row Classes
- `.jqgrow` - Data row
- `.ui-state-highlight` - Selected row
- `.ui-row-ltr` - Left-to-right row

### Custom Classes
- `.low-stock-row` - Example custom row class
- `.discontinued-row` - Example custom row class
- `.table-striped-row` - Alternating row color

## Events

### Grid Events
```javascript
tableInstance.$grid.on('jqGridLoadComplete', function(event) {});
tableInstance.$grid.on('jqGridSelectRow', function(event, rowid, status) {});
tableInstance.$grid.on('jqGridSelectAll', function(event, ids, status) {});
tableInstance.$grid.on('jqGridAfterInsertRow', function(event, rowid, data) {});
tableInstance.$grid.on('jqGridAfterDelRow', function(event, rowid) {});
```

### Custom Events
```javascript
$(document).on('jqgrid:bulkUpdate', function(event, data) {});
$(document).on('dataChanged', function(event, data) {});
```

## Quick Examples

### Basic Grid
```python
class ProductViewSet(JqGridConfigMixin, viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    visible_columns = ['id', 'name', 'price', 'in_stock']
    search_fields = ['name', 'description']
```

### Advanced Grid with All Features
```python
class AdvancedProductViewSet(JqGridConfigMixin, JqGridBulkActionMixin, viewsets.ModelViewSet):
    queryset = Product.objects.select_related('category')
    serializer_class = ProductSerializer
    
    # Columns
    visible_columns = ['id', 'name', 'category', 'price', 'quantity']
    frozen_columns = ['id', 'name']
    
    # Search and sort
    search_fields = ['name', 'category__name']
    ordering_fields = ['name', 'price', 'created_at']
    ordering = ['-created_at']
    
    # Grouping
    groupable_fields = ['category']
    
    # Bulk operations
    bulk_updateable_fields = ['price', 'category', 'status']
    
    # Formatting
    jqgrid_field_overrides = {
        'price': {'formatter': 'currency', 'formatoptions': {'prefix': '$'}}
    }
    
    conditional_formatting = {
        'quantity': [{'operator': 'lt', 'value': 5, 'backgroundColor': '#ffcccc'}]
    }
```

## Performance Tips

1. **Use select_related/prefetch_related**
   ```python
   queryset = Product.objects.select_related('category').prefetch_related('tags')
   ```

2. **Add database indexes**
   ```python
   class Meta:
       indexes = [
           models.Index(fields=['name', 'category']),
           models.Index(fields=['-created_at'])
       ]
   ```

3. **Limit visible columns**
   ```python
   visible_columns = ['id', 'name', 'price']  # Only show necessary columns
   ```

4. **Use caching**
   ```python
   from django.core.cache import cache
   
   def list(self, request, *args, **kwargs):
       cache_key = f"grid_{request.GET.urlencode()}"
       cached = cache.get(cache_key)
       if cached:
           return Response(cached)
       response = super().list(request, *args, **kwargs)
       cache.set(cache_key, response.data, 300)
       return response
   ```