# Django jqGrid Development Guide for Claude

This document provides context and guidelines for Claude when working on the django-jqgrid project.

## Project Overview

Django jqGrid is a comprehensive Django package that integrates jqGrid with Django REST Framework. It provides automatic grid configuration based on Django models and serializers, making it easy to create feature-rich data grids with minimal code.

## Quick Start Implementation Guide

### 1. Installation and Setup

```bash
# Install the package
pip install django-jqgrid

# Or install in development mode
pip install -e /path/to/django-jqgrid
```

**Add to settings.py:**
```python
INSTALLED_APPS = [
    # ... other apps
    'rest_framework',
    'django_filters',  # Optional but recommended
    'django_jqgrid',
    # ... your apps
]

# Optional: Add jqGrid specific settings
JQGRID_DEFAULT_ROWS = 25
JQGRID_MAX_ROWS = 1000

# Theme configuration
JQGRID_THEME = 'bootstrap4'  # Options: 'bootstrap', 'bootstrap4', 'bootstrap5', 'jqueryui'
JQGRID_ICON_SET = 'fontAwesome'  # Options: 'fontAwesome', 'bootstrap', 'jQueryUI', 'glyph'
JQGRID_CUSTOM_CSS = None  # Path to custom CSS file
```

**Add to urls.py:**
```python
from django.urls import path, include

urlpatterns = [
    # ... other patterns
    path('api/', include('your_app.urls')),  # Your API URLs
    path('api/grid/', include('django_jqgrid.urls')),  # Grid filter management
]
```

### 2. Basic Implementation Pattern

**models.py:**
```python
from django.db import models

class Product(models.Model):
    name = models.CharField(max_length=200)
    sku = models.CharField(max_length=50, unique=True)
    category = models.ForeignKey('Category', on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['name', 'sku']),
            models.Index(fields=['category', '-created_at']),
        ]
```

**serializers.py:**
```python
from rest_framework import serializers
from .models import Product

class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    
    class Meta:
        model = Product
        fields = '__all__'
```

**views.py:**
```python
from rest_framework import viewsets
from django_jqgrid.mixins import JqGridConfigMixin, JqGridBulkActionMixin
from .models import Product
from .serializers import ProductSerializer

class ProductViewSet(JqGridConfigMixin, JqGridBulkActionMixin, viewsets.ModelViewSet):
    queryset = Product.objects.select_related('category')
    serializer_class = ProductSerializer
    
    # Essential configuration
    visible_columns = ['id', 'sku', 'name', 'category', 'price', 'quantity', 'is_active']
    search_fields = ['name', 'sku', 'category__name']
    ordering_fields = ['name', 'price', 'quantity', 'created_at']
    ordering = ['-created_at']
    
    # Optional: Bulk operations
    bulk_updateable_fields = ['category', 'price', 'is_active']
```

**urls.py (app level):**
```python
from rest_framework.routers import DefaultRouter
from .views import ProductViewSet

router = DefaultRouter()
router.register(r'products', ProductViewSet)

urlpatterns = router.urls
```

**Template (products.html):**
```django
{% extends "base.html" %}
{% load static %}
{% load jqgrid_tags %}

{% block extra_css %}
    <!-- Option 1: Use default theme -->
    {% jqgrid_css %}
    
    <!-- Option 2: Use theme tag with parameters -->
    {% jqgrid_theme 'bootstrap4' 'fontAwesome' %}
    
    <!-- Option 3: Use settings-based theme -->
    {% jqgrid_theme %}
{% endblock %}

{% block content %}
    <div class="container-fluid">
        <div class="row">
            <div class="col-12">
                <div class="card">
                    <div class="card-body">
                        <table id="productGrid" class="jqGrid"></table>
                        <div id="productGridPager"></div>
                    </div>
                </div>
            </div>
        </div>
    </div>
{% endblock %}

{% block extra_js %}
    {% jqgrid_dependencies %}
    {% jqgrid_js %}
    
    <script>
    $(document).ready(function() {
        window.initializeTableInstance('productGrid', 'your_app', 'product', {
            pagerSelector: '#productGridPager'
        });
    });
    </script>
{% endblock %}
```

### 3. Common Customization Patterns

#### A. Field Formatting
```python
class ProductViewSet(JqGridConfigMixin, viewsets.ModelViewSet):
    # ... basic config ...
    
    jqgrid_field_overrides = {
        'price': {
            'formatter': 'currency',
            'formatoptions': {'prefix': '$', 'decimalPlaces': 2},
            'align': 'right',
            'width': 100
        },
        'is_active': {
            'formatter': 'checkbox',
            'align': 'center',
            'width': 80
        },
        'created_at': {
            'formatter': 'date',
            'formatoptions': {'newformat': 'Y-m-d'},
            'width': 120
        }
    }
```

#### B. Conditional Formatting
```python
conditional_formatting = {
    'quantity': [
        {
            'operator': 'eq',
            'value': 0,
            'backgroundColor': '#ffcccc',
            'textColor': '#cc0000'
        },
        {
            'operator': 'lt',
            'value': 10,
            'backgroundColor': '#fff3cd',
            'textColor': '#856404'
        }
    ]
}
```

#### C. Custom Actions
```python
@action(methods=['post'], detail=False)
def import_csv(self, request):
    """Import products from CSV"""
    file = request.FILES.get('file')
    # Process file...
    return Response({'imported': count})

@action(methods=['get'], detail=False)
def export_excel(self, request):
    """Export filtered products"""
    queryset = self.filter_queryset(self.get_queryset())
    # Generate Excel...
    return FileResponse(file)
```

#### D. Dynamic Configuration
```python
def get_visible_columns(self):
    """Show columns based on user permissions"""
    columns = ['id', 'name', 'price']
    
    if self.request.user.has_perm('view_costs'):
        columns.extend(['cost', 'profit_margin'])
    
    return columns

def get_jqgrid_config(self, request):
    self.visible_columns = self.get_visible_columns()
    return super().get_jqgrid_config(request)
```

### 4. JavaScript Customization

#### A. Custom Formatters
```javascript
// Register custom formatter
window.jqGridConfig.formatters.statusBadge = function(cellval, opts) {
    const colors = {
        'active': 'success',
        'pending': 'warning',
        'inactive': 'danger'
    };
    return `<span class="badge badge-${colors[cellval]}">${cellval}</span>`;
};
```

#### B. Hooks
```javascript
// Before grid initialization
window.jqGridConfig.hooks.beforeInitGrid = function(tableInstance) {
    // Add custom configuration
    tableInstance.options.rowNum = 50;
};

// After bulk update
window.jqGridConfig.hooks.afterSubmitBulkUpdate = function(tableInstance, ids, action, scope, response) {
    // Refresh dashboard
    updateDashboard();
};
```

#### C. Custom Buttons
```javascript
window.jqGridConfig.customButtons.product = [
    {
        id: 'import-products',
        label: 'Import',
        icon: 'fa-upload',
        class: 'btn-success',
        action: function(tableInstance) {
            $('#importModal').modal('show');
        }
    }
];
```

### 5. Performance Optimization Checklist

- [ ] Use `select_related()` for ForeignKey fields
- [ ] Use `prefetch_related()` for ManyToMany fields
- [ ] Add database indexes on searched/sorted fields
- [ ] Limit `visible_columns` to necessary fields only
- [ ] Use pagination (automatic with package)
- [ ] Consider caching for static data
- [ ] Use `only()` or `defer()` for large text fields

### 6. Security Checklist

- [ ] ViewSet has appropriate permission classes
- [ ] Bulk update fields are explicitly defined
- [ ] CSRF protection enabled (default in Django)
- [ ] User-specific filters use request.user
- [ ] Sensitive fields excluded from visible_columns
- [ ] Custom actions have permission checks

### 7. Common Issues and Solutions

**Issue: Grid not loading**
- Check browser console for JS errors
- Verify API endpoint returns data: `/api/your_app/product/`
- Check Django logs for permission errors

**Issue: Bulk operations not working**
- Ensure `JqGridBulkActionMixin` is included
- Check CSRF token in requests
- Verify `bulk_updateable_fields` is set

**Issue: Foreign key dropdowns empty**
- Check related model has __str__ method
- Verify user has permission to view related model
- Check API endpoint: `/api/related_app/related_model/`

**Issue: Custom formatter not working**
- Register formatter before grid initialization
- Check formatter name matches exactly
- Look for JS errors in formatter function

### 8. Advanced Features Quick Reference

**Grouping:**
```python
groupable_fields = ['category', 'status']
aggregation_fields = {
    'price': ['min', 'max', 'avg'],
    'quantity': ['sum']
}
```

**Frozen Columns:**
```python
frozen_columns = ['id', 'name']  # These columns stay fixed
```

**Row Highlighting:**
```python
highlight_rules = [
    {
        'field': 'quantity',
        'operator': 'eq',
        'value': 0,
        'cssClass': 'out-of-stock'
    }
]
```

**Custom CSS:**
```css
.out-of-stock {
    background-color: #ffe6e6 !important;
}

.jqgrid-dark-mode .ui-jqgrid {
    background-color: #1a1a1a;
    color: #e0e0e0;
}
```

### 9. Testing Strategies

**Python Tests:**
```python
def test_jqgrid_config(self):
    response = self.client.get('/api/products/jqgrid_config/')
    self.assertEqual(response.status_code, 200)
    config = response.json()
    self.assertIn('jqgrid_options', config)
    self.assertIn('colModel', config['jqgrid_options'])

def test_bulk_update(self):
    response = self.client.post('/api/products/bulk_action/', {
        'ids': [1, 2, 3],
        'action': {'price': 29.99}
    })
    self.assertEqual(response.status_code, 200)
```

**JavaScript Tests:**
```javascript
// Test custom formatter
QUnit.test("Status badge formatter", function(assert) {
    const result = window.jqGridConfig.formatters.statusBadge('active');
    assert.ok(result.includes('badge-success'), "Active status has success badge");
});
```

### 10. Deployment Checklist

- [ ] Static files collected: `python manage.py collectstatic`
- [ ] Database migrations applied
- [ ] Permissions configured for production users
- [ ] ALLOWED_HOSTS includes production domain
- [ ] DEBUG = False in production
- [ ] Caching configured for better performance
- [ ] Database indexes created
- [ ] Error logging configured


## Key Components

### 1. Core Python Modules
- **`mixins.py`**: Contains `JqGridConfigMixin` and `JqGridBulkActionMixin` - the main ViewSet mixins
- **`views.py`**: GridFilterViewSet for managing user-specific grid filters
- **`models.py`**: GridFilter model for storing custom user filters
- **`serializers.py`**: DRF serializers for grid configuration
- **`utils.py`**: Utility functions for jqGrid operations
- **`pagination.py`**: Custom pagination class optimized for jqGrid

### 2. JavaScript Files
- **`jqgrid-integration.js`**: Main integration layer between Django and jqGrid
- **`jqgrid-config.js`**: Default configuration settings
- **`jqgrid-core.js`**: Core functionality extensions

### 3. Static Assets
- **`plugins/jqGrid/`**: The jqGrid library files
- **`css/`**: Custom CSS for Bootstrap integration
- **Templates**: Django templates for grid rendering

## Development Guidelines

### When Adding New Features

1. **Check existing patterns**: Look at how similar features are implemented
2. **Maintain backward compatibility**: Don't break existing APIs
3. **Follow DRF conventions**: Use ViewSet actions, serializers, and permissions
4. **Update documentation**: Keep API_REFERENCE.md and docstrings current

### Code Style

#### Python
```python
# Use type hints where appropriate
def get_jqgrid_config(self, request: Request) -> Dict[str, Any]:
    """Generate jqGrid configuration from model metadata."""
    pass

# Follow PEP 8
# Use descriptive variable names
# Add docstrings to all public methods
```

#### JavaScript
```javascript
// Use consistent naming conventions
// camelCase for variables and functions
// PascalCase for classes
// Avoid global variables - use namespaces
```

### Common Tasks

#### Adding a New Grid Feature
1. Add configuration option to ViewSet mixin
2. Update `get_jqgrid_config` method to include new option
3. Add JavaScript handling in `jqgrid-integration.js`
4. Update documentation and examples

#### Debugging Grid Issues
1. Check browser console for JavaScript errors
2. Inspect network requests in Developer Tools
3. Verify ViewSet configuration and permissions
4. Check serializer field definitions

### Testing Considerations

When making changes:
1. Test with different Django/DRF versions (3.2+, DRF 3.12+)
2. Test with both Bootstrap 4 and Bootstrap 5 themes
3. Verify CRUD operations work correctly
4. Check bulk operations with large datasets
5. Ensure permissions are properly enforced

### Performance Optimization

Key areas to consider:
1. **Database queries**: Use select_related/prefetch_related
2. **Caching**: Content types and configurations are cached
3. **Pagination**: OptimizedPaginator avoids unnecessary counts
4. **JavaScript**: Minimize DOM manipulations

### Security Best Practices

1. **Always validate permissions** in ViewSet methods
2. **Sanitize user input** in filters and search
3. **Use CSRF protection** for all POST requests
4. **Validate bulk operations** field by field
5. **Never expose sensitive fields** without permission checks

## Project Structure

```
django_jqgrid/
├── __init__.py           # Package metadata, version info
├── apps.py               # Django app configuration
├── mixins.py            # Core ViewSet mixins
├── models.py            # GridFilter model
├── views.py             # GridFilterViewSet
├── serializers.py       # DRF serializers
├── utils.py             # Utility functions
├── pagination.py        # Custom pagination
├── urls.py              # URL patterns
├── admin.py             # Django admin integration
├── filters.py           # Custom DRF filters
├── static/              # Static files (CSS, JS)
│   ├── django_jqgrid/
│   │   ├── css/        # Custom styles
│   │   ├── js/         # Integration scripts
│   │   └── plugins/    # jqGrid library
├── templates/           # Django templates
├── templatetags/        # Custom template tags
└── migrations/          # Database migrations
```

## Version Information

Current version: 1.2.2

### Version History Highlights
- 1.2.x: Added grouping, frozen columns, conditional formatting
- 1.1.x: Bootstrap 5 support, real-time updates, inline editing
- 1.0.x: Initial release with core functionality

## Common Patterns

### ViewSet Configuration
```python
class ProductViewSet(JqGridConfigMixin, JqGridBulkActionMixin, viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    
    # Grid configuration
    visible_columns = ['id', 'name', 'price']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'price', 'created_at']
    
    # Bulk operations
    bulk_updateable_fields = ['price', 'status']
```

### JavaScript Integration
```javascript
// Always check for jQuery before using
if (typeof jQuery !== 'undefined') {
    $(document).ready(function() {
        // Initialize grid with config from API
        $.getJSON('/api/products/jqgrid_config/', function(config) {
            $("#jqGrid").jqGrid(config.jqgrid_options);
        });
    });
}
```

## Troubleshooting Tips

1. **Grid not loading**: Check browser console and network tab
2. **CRUD failures**: Verify CSRF token and permissions
3. **Performance issues**: Check database queries with Django Debug Toolbar
4. **CSS problems**: Ensure correct loading order of stylesheets

## Useful Commands

```bash
# Run example project
cd example_project
python manage.py runserver

# Build package
python -m build

# Run tests (when implemented)
python manage.py test django_jqgrid

# Check code style
flake8 django_jqgrid/
```

## External Resources

- [jqGrid Documentation](http://www.trirand.com/jqgridwiki/doku.php)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [Bootstrap jqGrid Themes](http://www.trirand.com/blog/?page_id=6)

## Quick Decision Guide

### When to Use django-jqgrid

✅ **Perfect for:**
- Admin interfaces and internal tools
- Data-heavy applications with complex filtering needs
- Reports and analytics dashboards
- CRUD operations on large datasets
- When you need Excel-like functionality in web

❌ **Not ideal for:**
- Public-facing websites (heavy JS library)
- Simple lists (< 100 items)
- Mobile-first applications
- When you need custom UI/UX

### Feature Selection Guide

| Feature | When to Use | Performance Impact |
|---------|-------------|-------------------|
| **Grouping** | Categories/hierarchical data | Medium - adds complexity |
| **Frozen Columns** | Wide tables with key fields | Low - CSS based |
| **Bulk Operations** | Admin/power users | Low - server side |
| **Conditional Formatting** | Visual data analysis | Low - client side |
| **Real-time Updates** | Live dashboards | High - requires WebSocket |
| **Excel Export** | Reporting requirements | Medium - server processing |

### Architecture Patterns

#### 1. Simple CRUD Pattern
```python
# Best for: Basic data management
class SimpleViewSet(JqGridConfigMixin, viewsets.ModelViewSet):
    queryset = Model.objects.all()
    serializer_class = ModelSerializer
    visible_columns = ['id', 'name', 'status']
    search_fields = ['name']
```

#### 2. Read-Only Analytics Pattern
```python
# Best for: Dashboards, reports
class AnalyticsViewSet(JqGridConfigMixin, viewsets.ReadOnlyModelViewSet):
    queryset = Model.objects.annotate(
        total=Sum('amount'),
        avg_value=Avg('value')
    )
    serializer_class = AnalyticsSerializer
    groupable_fields = ['category', 'date']
    aggregation_fields = {'total': ['sum'], 'count': ['count']}
```

#### 3. Multi-Tenant Pattern
```python
# Best for: SaaS applications
class TenantViewSet(JqGridConfigMixin, viewsets.ModelViewSet):
    def get_queryset(self):
        return Model.objects.filter(
            tenant=self.request.user.tenant
        )
    
    def perform_create(self, serializer):
        serializer.save(tenant=self.request.user.tenant)
```

### Integration Examples

#### With Django Admin
```python
# admin.py
from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    change_list_template = 'admin/product_changelist.html'
    
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['jqgrid_url'] = reverse('product-list')
        return super().changelist_view(request, extra_context)
```

#### With Django Channels (Real-time)
```python
# consumers.py
class GridConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.grid_name = self.scope['url_route']['kwargs']['grid_name']
        await self.channel_layer.group_add(
            f'grid_{self.grid_name}',
            self.channel_name
        )
        await self.accept()
    
    async def grid_update(self, event):
        await self.send(text_data=json.dumps({
            'type': 'update',
            'data': event['data']
        }))
```

#### With Celery (Background Tasks)
```python
# tasks.py
@shared_task
def export_grid_data(viewset_class, filters, user_id):
    viewset = viewset_class()
    viewset.request = MockRequest(user_id=user_id)
    queryset = viewset.filter_queryset(viewset.get_queryset())
    
    # Generate Excel
    df = pd.DataFrame(queryset.values())
    file_path = f'/tmp/export_{user_id}.xlsx'
    df.to_excel(file_path)
    
    # Send email with file
    send_export_email.delay(user_id, file_path)
```

### Code Snippets Library

#### 1. Custom Cell Editor
```javascript
// Date picker cell editor
function createDateEditor(value, options) {
    const input = $('<input type="text" class="form-control">');
    input.val(value);
    input.datepicker({
        dateFormat: 'yy-mm-dd',
        onSelect: function(dateText) {
            $(this).trigger('change');
        }
    });
    return input;
}
```

#### 2. Row Actions Column
```python
def initialize_columns(self):
    super().initialize_columns()
    
    # Add actions column
    self.colmodel.append({
        'name': 'actions',
        'label': 'Actions',
        'formatter': 'actions',
        'formatoptions': {
            'keys': True,
            'editformbutton': True,
            'delbutton': True,
            'delOptions': {
                'url': f'/api/{self.model_name}/{{id}}/',
                'afterSubmit': 'handleDeleteResponse'
            }
        },
        'width': 120,
        'fixed': True,
        'sortable': False,
        'search': False
    })
```

#### 3. Custom Search Widget
```javascript
// Autocomplete search
function createAutocompleteSearch(elem, options) {
    $(elem).autocomplete({
        source: function(request, response) {
            $.ajax({
                url: '/api/search/',
                data: { term: request.term },
                success: function(data) {
                    response(data.results);
                }
            });
        },
        minLength: 2,
        select: function(event, ui) {
            const grid = $('#grid');
            grid.jqGrid('setGridParam', {
                postData: { custom_search: ui.item.value }
            }).trigger('reloadGrid');
        }
    });
}
```

#### 4. Export with Formatting
```python
@action(methods=['get'], detail=False)
def export_formatted(self, request):
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill
    
    queryset = self.filter_queryset(self.get_queryset())
    
    wb = Workbook()
    ws = wb.active
    
    # Headers
    headers = ['ID', 'Name', 'Price', 'Status']
    for col, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col, value=header)
        cell.font = Font(bold=True)
        cell.fill = PatternFill(start_color="CCCCCC", fill_type="solid")
    
    # Data
    for row, obj in enumerate(queryset, 2):
        ws.cell(row=row, column=1, value=obj.id)
        ws.cell(row=row, column=2, value=obj.name)
        ws.cell(row=row, column=3, value=obj.price)
        ws.cell(row=row, column=4, value=obj.status)
        
        # Conditional formatting
        if obj.status == 'inactive':
            for col in range(1, 5):
                ws.cell(row=row, column=col).fill = PatternFill(
                    start_color="FFCCCC", fill_type="solid"
                )
    
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=products.xlsx'
    wb.save(response)
    return response
```

### Debugging Guide

#### 1. Enable Debug Mode
```javascript
// Add to your base template
window.jqGridConfig.debug = true;
window.jqGridConfig.hooks.beforeInitGrid = function(tableInstance) {
    console.log('Grid Config:', tableInstance);
};
```

#### 2. API Debugging
```python
# Add to ViewSet for debugging
def list(self, request, *args, **kwargs):
    print(f"Query params: {request.query_params}")
    print(f"Filters: {request.query_params.get('filters')}")
    response = super().list(request, *args, **kwargs)
    print(f"Response count: {len(response.data.get('data', []))}")
    return response
```

#### 3. Performance Profiling
```python
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from silk.profiling.profiler import silk_profile

class ProfiledViewSet(JqGridConfigMixin, viewsets.ModelViewSet):
    @silk_profile(name='Grid List View')
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @method_decorator(cache_page(60 * 5))  # Cache for 5 minutes
    @action(methods=['get'], detail=False)
    def jqgrid_config(self, request, *args, **kwargs):
        return super().jqgrid_config(request, *args, **kwargs)
```

### Migration Guide

#### From DataTables
```python
# DataTables pattern
data = {
    'data': queryset.values(),
    'draw': request.GET.get('draw'),
    'recordsTotal': total,
    'recordsFiltered': filtered
}

# jqGrid equivalent (automatic with package)
class ViewSet(JqGridConfigMixin, viewsets.ModelViewSet):
    # Pagination handled automatically
    # Just define queryset and serializer
```

#### From Manual jQuery
```javascript
// Old jQuery pattern
$.ajax({
    url: '/api/data/',
    success: function(data) {
        var table = '<table>';
        $.each(data, function(i, row) {
            table += '<tr><td>' + row.name + '</td></tr>';
        });
        table += '</table>';
        $('#container').html(table);
    }
});

// jqGrid pattern
window.initializeTableInstance('grid', 'app', 'model');
// All functionality automatic
```

## Notes for Future Development

1. Consider adding TypeScript definitions for better IDE support
2. Explore WebSocket integration for real-time updates
3. Add more comprehensive test suite
4. Consider creating a demo site with live examples
5. Add support for newer grid libraries as alternatives
6. Create Vue.js/React wrapper components
7. Add GraphQL support alongside REST
8. Implement smart caching strategies
9. Add data validation hooks
10. Create grid templates for common use cases

Remember: The goal is to make data grid implementation as simple as possible while maintaining flexibility for advanced use cases.