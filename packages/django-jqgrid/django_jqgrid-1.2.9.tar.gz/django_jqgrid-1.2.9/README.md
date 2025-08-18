# Django jqGrid Package

A comprehensive Django package that provides seamless integration of jqGrid with Django REST Framework, offering powerful data grid functionality with minimal configuration.

## Features

- **Automatic Configuration**: Generates jqGrid configuration from Django model metadata and DRF serializers
- **Full CRUD Support**: Built-in Create, Read, Update, Delete operations via REST API
- **Advanced Features**:
  - Multi-column sorting
  - Advanced filtering with multiple operators
  - Bulk operations (update/delete)
  - Row grouping and aggregation
  - Frozen columns
  - Conditional formatting
  - Import/Export functionality
  - Custom grid filters per user
- **Responsive Design**: Bootstrap 4/5 compatible with mobile support
- **Security**: Permission-based access control
- **Extensible**: Easy to customize and extend

## Installation

```bash
pip install django-jqgrid
```

## Quick Start

### 1. Add to Installed Apps

```python
INSTALLED_APPS = [
    # ...
    'rest_framework',
    'django_jqgrid',
    # ...
]
```

### 2. Include URLs

```python
# urls.py
from django.urls import path, include

urlpatterns = [
    # ...
    path('api/grid/', include('django_jqgrid.urls')),
    # ...
]
```

### 3. Create a ViewSet with JqGrid Mixin

```python
# views.py
from rest_framework import viewsets
from django_jqgrid.mixins import JqGridConfigMixin, JqGridBulkActionMixin
from .models import YourModel
from .serializers import YourModelSerializer

class YourModelViewSet(JqGridConfigMixin, JqGridBulkActionMixin, viewsets.ModelViewSet):
    queryset = YourModel.objects.all()
    serializer_class = YourModelSerializer
    
    # Optional: Customize visible columns
    visible_columns = ['id', 'name', 'email', 'created_at']
    
    # Optional: Define searchable fields
    search_fields = ['name', 'email']
    
    # Optional: Define sortable fields
    ordering_fields = ['name', 'created_at']
    
    # Optional: Default ordering
    ordering = ['-created_at']
```

### 4. Add jqGrid to Your Template

```html
<!-- Include jQuery and jqGrid files -->
<link rel="stylesheet" href="{% static 'django_jqgrid/plugins/jqGrid/css/ui.jqgrid-bootstrap4.css' %}">
<script src="{% static 'django_jqgrid/plugins/jqGrid/js/jquery.jqGrid.min.js' %}"></script>
<script src="{% static 'django_jqgrid/js/jqgrid-integration.js' %}"></script>

<!-- Grid Container -->
<table id="jqGrid"></table>
<div id="jqGridPager"></div>

<script>
$(document).ready(function() {
    // Initialize jqGrid with configuration from API
    $.getJSON('/api/yourapp/yourmodel/jqgrid_config/', function(config) {
        $("#jqGrid").jqGrid(config.jqgrid_options);
        
        // Apply method options
        $("#jqGrid").jqGrid('navGrid', '#jqGridPager', 
            config.method_options.navGrid.options,
            config.method_options.navGrid.editOptions,
            config.method_options.navGrid.addOptions,
            config.method_options.navGrid.delOptions,
            config.method_options.navGrid.searchOptions,
            config.method_options.navGrid.viewOptions
        );
        
        // Apply filter toolbar
        $("#jqGrid").jqGrid('filterToolbar', config.method_options.filterToolbar.options);
    });
});
</script>
```

## Configuration

### Serializer-Based Configuration

The package automatically configures jqGrid based on your DRF serializer fields:

```python
from rest_framework import serializers
from .models import Product

class ProductSerializer(serializers.ModelSerializer):
    # Read-only fields become non-editable in grid
    total_sales = serializers.ReadOnlyField()
    
    # Custom labels are used in grid headers
    name = serializers.CharField(label="Product Name")
    
    # Field types determine grid column types
    price = serializers.DecimalField(max_digits=10, decimal_places=2)
    in_stock = serializers.BooleanField()
    created_at = serializers.DateTimeField(read_only=True)
    
    class Meta:
        model = Product
        fields = ['id', 'name', 'price', 'in_stock', 'total_sales', 'created_at']
```

### Field Type Mappings

The package automatically maps Django field types to jqGrid column configurations:

| Django Field Type | jqGrid Configuration |
|------------------|---------------------|
| CharField | `stype: 'text'`, search operators: eq, ne, cn, nc, bw, bn, ew, en |
| IntegerField | `stype: 'integer'`, `align: 'right'`, search operators: eq, ne, lt, le, gt, ge |
| DecimalField | `stype: 'number'`, `align: 'right'`, with decimal places |
| BooleanField | `stype: 'checkbox'`, `align: 'center'` |
| DateField | `stype: 'date'`, with datepicker |
| DateTimeField | `stype: 'datetime-local'`, with datetimepicker |
| ForeignKey | `stype: 'select'`, with dropdown data URL |
| EmailField | `stype: 'email'`, `formatter: 'email'` |
| URLField | `stype: 'text'`, `formatter: 'link'` |

### ViewSet Configuration Options

```python
class ProductViewSet(JqGridConfigMixin, JqGridBulkActionMixin, viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    
    # Column visibility
    visible_columns = ['id', 'name', 'price', 'in_stock', 'created_at']
    
    # Search configuration
    search_fields = ['name', 'description', 'sku']
    
    # Sorting configuration
    ordering_fields = ['name', 'price', 'created_at']
    ordering = ['-created_at', 'name']  # Default sort
    
    # Grouping configuration
    groupable_fields = ['category', 'brand']
    
    # Frozen columns (stay visible when scrolling)
    frozen_columns = ['id', 'name']
    
    # Bulk operations
    bulk_updateable_fields = ['price', 'in_stock', 'category']
    bulk_actions = [
        {
            'id': 'bulk-update-price',
            'label': 'Update Price',
            'icon': 'fa-dollar',
            'class': 'btn-warning'
        },
        {
            'id': 'bulk-delete',
            'label': 'Delete Selected',
            'icon': 'fa-trash',
            'class': 'btn-danger'
        }
    ]
    
    # Field overrides
    jqgrid_field_overrides = {
        'price': {
            'formatter': 'currency',
            'formatoptions': {'prefix': '$', 'decimalPlaces': 2}
        }
    }
    
    # Grid options override
    jqgrid_options_override = {
        'rowNum': 50,
        'height': 600,
        'caption': 'Product Inventory'
    }
    
    # Conditional formatting
    conditional_formatting = {
        'in_stock': {
            'false': {'color': 'red', 'background': '#ffeeee'},
            'true': {'color': 'green', 'background': '#eeffee'}
        },
        'price': {
            'condition': 'value > 1000',
            'style': {'fontWeight': 'bold', 'color': 'blue'}
        }
    }
```

## Advanced Features

### 1. Bulk Operations

The `JqGridBulkActionMixin` provides bulk update and delete functionality:

```javascript
// Bulk update example
$.ajax({
    url: '/api/products/bulk_action/',
    method: 'POST',
    data: JSON.stringify({
        ids: [1, 2, 3],
        action: {
            price: 29.99,
            in_stock: true
        }
    }),
    contentType: 'application/json'
});

// Bulk delete example
$.ajax({
    url: '/api/products/bulk_action/',
    method: 'POST',
    data: JSON.stringify({
        ids: [1, 2, 3],
        action: {
            _delete: true
        }
    }),
    contentType: 'application/json'
});
```

### 2. Custom Grid Filters

Users can save and manage custom grid filters:

```python
# The package includes GridFilter model for storing user filters
from django_jqgrid.models import GridFilter

# Filters are automatically available in the grid search dialog
# Users can save search criteria as named filters
```

### 3. Import/Export Configuration

```python
class ProductViewSet(JqGridConfigMixin, viewsets.ModelViewSet):
    # ... other configuration ...
    
    import_config = {
        'supported_formats': ['csv', 'xlsx', 'json'],
        'field_mapping': {
            'Product Name': 'name',
            'Price': 'price',
            'Stock': 'in_stock'
        }
    }
    
    export_config = {
        'formats': ['csv', 'xlsx', 'pdf'],
        'include_headers': True,
        'max_rows': 10000
    }
```

### 4. Row Grouping

```python
class OrderViewSet(JqGridConfigMixin, viewsets.ModelViewSet):
    # ... other configuration ...
    
    groupable_fields = ['status', 'customer', 'date']
    aggregation_fields = {
        'total': 'sum',
        'items_count': 'count'
    }
```

## API Endpoints

The package automatically creates these endpoints for each model:

- `GET /api/<app>/<model>/` - List/search records with jqGrid parameters
- `GET /api/<app>/<model>/jqgrid_config/` - Get grid configuration
- `POST /api/<app>/<model>/crud/` - Handle jqGrid CRUD operations
- `POST /api/<app>/<model>/bulk_action/` - Bulk update/delete
- `GET /api/<app>/<model>/dropdown/` - Get dropdown data for foreign keys

## Settings

```python
# settings.py

# Default grid options (optional)
JQGRID_DEFAULT_GRID_OPTIONS = {
    'rowNum': 25,
    'rowList': [25, 50, 100, 500, 1000],
    'height': 400,
    'styleUI': 'Bootstrap4',
    'iconSet': 'fontAwesome'
}

# Default field type configurations (optional)
JQGRID_DEFAULT_FIELD_CONFIG = {
    'DateField': {
        'formatoptions': {"srcformat": "ISO8601Short", "newformat": "d/m/Y"}
    }
}
```

## JavaScript Integration

The package includes JavaScript utilities for enhanced functionality:

```javascript
// jqgrid-integration.js provides helper functions

// Handle form responses
window.handleFormResponse = function(response, postdata) {
    // Custom response handling
};

// Handle export
window.handleExport = function() {
    // Export grid data
};

// Handle import
window.handleImport = function() {
    // Import data dialog
};
```

## Theme Configuration

Django jqGrid supports multiple themes and can be easily customized to match your application's design.

### Using the Theme Template Tag

```django
{% load jqgrid_tags %}

<!-- Use default theme (Bootstrap 4) -->
{% jqgrid_theme %}

<!-- Specify theme and icon set -->
{% jqgrid_theme 'bootstrap5' 'fontAwesome' %}

<!-- Use custom CSS -->
{% jqgrid_theme theme='bootstrap4' custom_css='/static/css/my-grid-theme.css' %}
```

### Available Themes

- **bootstrap** - Bootstrap 3 theme
- **bootstrap4** - Bootstrap 4 theme (default)
- **bootstrap5** - Bootstrap 5 theme
- **jqueryui** - jQuery UI theme

### Available Icon Sets

- **fontAwesome** - Font Awesome icons (default)
- **bootstrap** - Bootstrap Icons
- **jQueryUI** - jQuery UI icons
- **glyph** - Glyphicons (Bootstrap 3)

### Settings-Based Configuration

Configure theme globally in your Django settings:

```python
# settings.py
JQGRID_THEME = 'bootstrap5'
JQGRID_ICON_SET = 'fontAwesome'
JQGRID_CUSTOM_CSS = '/static/css/custom-grid.css'
```

### Dynamic Theme Switching

Include the theme switcher component:

```html
<!-- Theme switcher container -->
<div id="theme-switcher"></div>

<!-- Include theme switcher JS -->
<script src="{% static 'django_jqgrid/js/jqgrid-theme-switcher.js' %}"></script>

<script>
// Initialize theme switcher
jqGridThemeSwitcher.init({
    container: '#theme-switcher',
    showPreview: true,
    onChange: function(theme, iconSet) {
        console.log('Theme changed to:', theme, iconSet);
    }
});
</script>
```

### Custom Theme CSS

Create your own theme by overriding CSS variables:

```css
/* custom-grid-theme.css */
:root {
    /* Grid colors */
    --jqgrid-header-bg: #2c3e50;
    --jqgrid-header-text: #ffffff;
    --jqgrid-row-hover: #ecf0f1;
    --jqgrid-row-selected: #3498db;
    
    /* Borders */
    --jqgrid-border-color: #bdc3c7;
    
    /* Fonts */
    --jqgrid-font-size: 14px;
    --jqgrid-header-font-weight: 600;
}

/* Dark mode support */
@media (prefers-color-scheme: dark) {
    :root {
        --jqgrid-header-bg: #1a1a1a;
        --jqgrid-row-bg: #2a2a2a;
        --jqgrid-row-alt-bg: #333333;
    }
}
```

## Customization and Extension

Django jqGrid is designed to be highly customizable. Here are some common customization examples:

### Quick Customization Examples

#### 1. Custom Formatters
```javascript
// Register a custom status badge formatter
window.jqGridConfig.formatters.statusBadge = function(cellval, opts) {
    const statusClasses = {
        'active': 'badge-success',
        'pending': 'badge-warning',
        'inactive': 'badge-danger'
    };
    const badgeClass = statusClasses[cellval] || 'badge-info';
    return `<span class="badge ${badgeClass}">${cellval}</span>`;
};

// Use in ViewSet
jqgrid_field_overrides = {
    'status': {
        'formatter': 'statusBadge',
        'align': 'center'
    }
}
```

#### 2. Custom Bulk Actions
```python
class ProductViewSet(JqGridConfigMixin, JqGridBulkActionMixin, viewsets.ModelViewSet):
    # Define custom bulk actions
    bulk_actions = [
        {
            'id': 'apply-discount',
            'label': 'Apply Discount',
            'icon': 'fa-percent',
            'class': 'btn-warning'
        }
    ]
    
    @action(methods=['post'], detail=False)
    def bulk_action(self, request):
        action_id = request.data.get('action_id')
        if action_id == 'apply-discount':
            # Custom logic here
            return Response({'status': 'success'})
        return super().bulk_action(request)
```

#### 3. JavaScript Hooks
```javascript
// Customize grid behavior using hooks
window.jqGridConfig.hooks.beforeInitGrid = function(tableInstance) {
    // Add custom configuration before grid initializes
    tableInstance.options.customData = { department: 'sales' };
};

window.jqGridConfig.hooks.afterSubmitBulkUpdate = function(tableInstance, ids, action, scope, response) {
    // Custom notification after bulk update
    showCustomNotification('Updated ' + ids.length + ' records');
};
```

#### 4. Dynamic Column Configuration
```python
class UserAwareProductViewSet(JqGridConfigMixin, viewsets.ModelViewSet):
    def get_visible_columns(self):
        """Show different columns based on user permissions"""
        base_columns = ['id', 'name', 'price']
        
        if self.request.user.has_perm('products.view_cost'):
            base_columns.extend(['cost', 'profit_margin'])
        
        if self.request.user.is_staff:
            base_columns.extend(['supplier', 'internal_notes'])
        
        return base_columns
    
    def get_jqgrid_config(self, request):
        self.visible_columns = self.get_visible_columns()
        return super().get_jqgrid_config(request)
```

#### 5. Custom Toolbar Buttons
```javascript
// Add custom buttons to specific tables
window.jqGridConfig.customButtons.product = [
    {
        id: 'import-csv',
        label: 'Import CSV',
        icon: 'fa-file-csv',
        class: 'btn-success',
        action: function(tableInstance) {
            showImportModal(tableInstance);
        }
    }
];
```

### Complete Customization Guide

For comprehensive customization examples including:
- Advanced ViewSet customization
- Custom field types
- Theme customization
- Real-time updates
- Performance optimization
- Complex real-world examples

See the [**Customization Guide**](CUSTOMIZATION_GUIDE.md).

## Example Project

The package includes a complete example project demonstrating all features:

### Running the Example Project

```bash
# Navigate to example project
cd example_project

# Install dependencies
pip install -r requirements.txt

# Setup the project
python setup_example.py

# Run the server
python manage.py runserver
```

Visit: `http://localhost:8000/`

## Security

- All operations respect Django's permission system
- CSRF protection for all POST requests
- User-specific filters are isolated
- Bulk operations validate field permissions

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)
- Mobile browsers (responsive mode)

## Troubleshooting

### Common Issues

#### 1. "jqgrid_tags is not a registered tag library"
**Solution:**
- Ensure `django_jqgrid` is in your `INSTALLED_APPS`
- Restart the Django development server
- If developing locally, install the package in editable mode: `pip install -e .`

#### 2. Grid not loading data
**Solution:**
- Check browser console for JavaScript errors
- Verify the API endpoint is accessible
- Ensure DRF permissions allow access
- Check that the ViewSet URL pattern is correct

#### 3. Bulk operations not working
**Solution:**
- Verify `JqGridBulkActionMixin` is included in your ViewSet
- Check CSRF token is being sent with requests
- Ensure user has appropriate permissions

#### 4. Custom formatters not displaying
**Solution:**
- Register formatters before grid initialization
- Check formatter function name matches configuration
- Verify no JavaScript errors in formatter function

#### 5. Performance issues with large datasets
**Solution:**
- Use server-side pagination (enabled by default)
- Add database indexes on frequently sorted/filtered columns
- Use `select_related()` and `prefetch_related()` in querysets
- Consider implementing caching for frequently accessed data

For more detailed troubleshooting, see the [Customization Guide](CUSTOMIZATION_GUIDE.md#troubleshooting).

## Documentation

- [Installation Guide](INSTALLATION_GUIDE.md) - Detailed installation instructions
- [Configuration Guide](CONFIGURATION_GUIDE.md) - Complete configuration reference
- [Features Guide](FEATURES_GUIDE.md) - Comprehensive feature documentation and how to enable them
- [Customization Guide](CUSTOMIZATION_GUIDE.md) - Advanced customization options
- [JavaScript Hooks](JAVASCRIPT_HOOKS.md) - Client-side extensibility
- [API Reference](API_REFERENCE.md) - Complete API documentation
- [Troubleshooting](TROUBLESHOOTING.md) - Common issues and solutions

## Requirements

- Python 3.8+
- Django 3.2+
- Django REST Framework 3.12+

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

For issues and feature requests, please use the [GitHub issue tracker](https://github.com/coder-aniket/django-jqgrid/issues).