# Django jqGrid Features Quick Reference

## Essential Features (Enabled by Default)

| Feature | ViewSet Property | Template Tag | Notes |
|---------|-----------------|--------------|-------|
| **Sorting** | `ordering_fields = ['name', 'price']` | N/A | All visible columns sortable by default |
| **Searching** | `search_fields = ['name', 'description']` | N/A | Text search across specified fields |
| **Pagination** | `page_size = 25` | N/A | Automatic with customizable page sizes |
| **Column Resizing** | N/A | N/A | Enabled by default |
| **Row Selection** | `multiselect = True` | N/A | Single/multi selection support |

## Advanced Features (Opt-in)

| Feature | How to Enable | Configuration | Example |
|---------|--------------|---------------|---------|
| **Bulk Operations** | Add `JqGridBulkActionMixin` | `bulk_updateable_fields = ['price', 'status']` | [See example](#bulk-operations-example) |
| **Inline Editing** | `enable_inline_editing = True` | `editable_fields = ['name', 'price']` | [See example](#inline-editing-example) |
| **Grouping** | `enable_grouping = True` | `groupable_fields = ['category']` | [See example](#grouping-example) |
| **Export** | `enable_export = True` | `export_formats = ['excel', 'csv']` | [See example](#export-example) |
| **Import** | `enable_import = True` | `import_config = {...}` | [See example](#import-example) |
| **Frozen Columns** | `frozen_columns = ['id', 'name']` | N/A | Columns stay fixed during scroll |
| **Subgrids** | `enable_subgrid = True` | `subgrid_config = {...}` | [See example](#subgrid-example) |
| **Filter Toolbar** | `enable_filter_toolbar = True` | N/A | Column-specific filters |
| **Column Chooser** | `enable_column_chooser = True` | `available_columns = [...]` | Show/hide columns |
| **Tree Grid** | `enable_tree_grid = True` | `tree_config = {...}` | Hierarchical data |

## Settings.py Configuration

```python
# Core settings
JQGRID_DEFAULT_ROWS = 25
JQGRID_MAX_ROWS = 1000
JQGRID_THEME = 'bootstrap4'  # bootstrap, bootstrap4, bootstrap5, jqueryui
JQGRID_ICON_SET = 'fontAwesome'  # fontAwesome, bootstrap, jQueryUI, glyph

# Global feature flags
JQGRID_FEATURES = {
    'ENABLE_BULK_OPERATIONS': True,
    'ENABLE_INLINE_EDITING': True,
    'ENABLE_EXPORT': True,
    'ENABLE_IMPORT': True,
    'ENABLE_GROUPING': True,
    'ENABLE_COLUMN_CHOOSER': True,
}
```

## Quick Examples

### Bulk Operations Example
```python
from django_jqgrid.mixins import JqGridConfigMixin, JqGridBulkActionMixin

class ProductViewSet(JqGridConfigMixin, JqGridBulkActionMixin, viewsets.ModelViewSet):
    bulk_updateable_fields = ['price', 'category', 'is_active']
    
    bulk_actions = [
        {'id': 'bulk-delete', 'label': 'Delete', 'icon': 'fa-trash'},
        {'id': 'bulk-update', 'label': 'Update', 'icon': 'fa-edit'},
    ]
```

### Inline Editing Example
```python
class ProductViewSet(JqGridConfigMixin, viewsets.ModelViewSet):
    enable_inline_editing = True
    editable_fields = ['name', 'price', 'quantity']
    
    jqgrid_field_overrides = {
        'price': {
            'editable': True,
            'editrules': {'required': True, 'number': True, 'minValue': 0}
        }
    }
```

### Grouping Example
```python
class ProductViewSet(JqGridConfigMixin, viewsets.ModelViewSet):
    enable_grouping = True
    groupable_fields = ['category', 'status']
    
    aggregation_fields = {
        'price': ['min', 'max', 'avg'],
        'quantity': ['sum']
    }
```

### Export Example
```python
class ProductViewSet(JqGridConfigMixin, viewsets.ModelViewSet):
    enable_export = True
    export_formats = ['excel', 'csv', 'pdf']
    
    export_config = {
        'excel': {'include_headers': True, 'freeze_headers': True},
        'csv': {'delimiter': ',', 'encoding': 'utf-8'}
    }
```

### Import Example
```python
class ProductViewSet(JqGridConfigMixin, viewsets.ModelViewSet):
    enable_import = True
    
    import_config = {
        'allowed_formats': ['xlsx', 'csv'],
        'preview_rows': 10,
        'update_existing': True,
        'unique_fields': ['sku']
    }
```

### Subgrid Example
```python
class OrderViewSet(JqGridConfigMixin, viewsets.ModelViewSet):
    enable_subgrid = True
    
    @action(detail=True, methods=['get'])
    def items(self, request, pk=None):
        order = self.get_object()
        items = order.items.all()
        serializer = OrderItemSerializer(items, many=True)
        return Response(serializer.data)
```

## JavaScript Feature Control

```javascript
// Initialize with features
window.initializeTableInstance('productGrid', 'app', 'product', {
    features: {
        enableGrouping: true,
        enableFrozenColumns: true,
        enableAutoSave: true
    }
});

// Global feature configuration
window.jqGridConfig.features = {
    enableTooltips: true,
    enableKeyboardNavigation: true,
    confirmDelete: true
};
```

## Template Tags

```django
{% load jqgrid_tags %}

{# Basic grid #}
{% jqgrid "grid_id" "app_name" "model_name" %}

{# Grid with features #}
{% jqgrid "grid_id" "app_name" "model_name" 
    include_import_export=True 
    enable_grouping=True 
%}

{# Theme configuration #}
{% jqgrid_theme 'bootstrap5' 'fontAwesome' %}
```

## Feature Dependencies

- **Cell Editing** requires **Inline Editing**
- **Import** requires **Bulk Operations**
- **Filter Save** requires **Filter Toolbar**
- **Virtual Scroll** recommended for 1000+ rows

## Performance Tips

- Use `select_related()` for ForeignKey fields
- Use `prefetch_related()` for ManyToMany fields
- Enable virtual scrolling for large datasets
- Add database indexes on searched/sorted columns
- Limit `visible_columns` to necessary fields

For complete documentation, see the [Features Guide](FEATURES_GUIDE.md).