# Django jqGrid Customization Guide

This guide shows how to extend and customize django-jqgrid features in your own projects.

## Table of Contents
1. [Basic Customization](#basic-customization)
2. [Advanced ViewSet Customization](#advanced-viewset-customization)
3. [JavaScript Hooks and Extensions](#javascript-hooks-and-extensions)
4. [Custom Field Types](#custom-field-types)
5. [Custom Bulk Actions](#custom-bulk-actions)
6. [Custom Formatters](#custom-formatters)
7. [Custom Toolbar Buttons](#custom-toolbar-buttons)
8. [Theme Customization](#theme-customization)
9. [Real-World Examples](#real-world-examples)

## Basic Customization

### 1. Customizing Grid Options

Override default grid options in your ViewSet:

```python
from django_jqgrid.mixins import JqGridConfigMixin, JqGridBulkActionMixin
from rest_framework import viewsets
from .models import Product
from .serializers import ProductSerializer

class ProductViewSet(JqGridConfigMixin, JqGridBulkActionMixin, viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    
    # Basic configuration
    visible_columns = ['id', 'name', 'price', 'category', 'in_stock']
    search_fields = ['name', 'description', 'category__name']
    ordering_fields = ['name', 'price', 'created_at']
    ordering = ['-created_at']  # Default ordering
    
    # Override grid options
    jqgrid_options_override = {
        'height': 600,
        'rowNum': 50,
        'rowList': [25, 50, 100, 200],
        'caption': 'Product Inventory Management',
        'viewrecords': True,
        'altRows': True,
        'altclass': 'table-striped-row'
    }
    
    # Override method options
    method_options_override = {
        'navGrid': {
            'options': {
                'add': True,
                'edit': True,
                'del': True,
                'search': True,
                'refresh': True
            }
        }
    }
```

### 2. Field-Specific Configuration

Customize individual field behavior:

```python
class ProductViewSet(JqGridConfigMixin, viewsets.ModelViewSet):
    # ... other configuration ...
    
    # Field-specific overrides
    jqgrid_field_overrides = {
        'price': {
            'formatter': 'currency',
            'formatoptions': {'decimalPlaces': 2, 'prefix': '$'},
            'align': 'right',
            'width': 100
        },
        'in_stock': {
            'formatter': 'checkbox',
            'align': 'center',
            'width': 80,
            'edittype': 'checkbox',
            'editoptions': {'value': '1:0'}
        },
        'category': {
            'stype': 'select',
            'searchoptions': {
                'dataUrl': '/api/categories/dropdown/',
                'sopt': ['eq', 'ne']
            }
        },
        'created_at': {
            'formatter': 'date',
            'formatoptions': {'newformat': 'd/m/Y'},
            'width': 120
        }
    }
```

## Advanced ViewSet Customization

### 1. Custom Column Configuration

Override the `initialize_columns` method for complete control:

```python
class AdvancedProductViewSet(JqGridConfigMixin, viewsets.ModelViewSet):
    # ... basic configuration ...
    
    def initialize_columns(self):
        # Call parent method first
        super().initialize_columns()
        
        # Add custom computed columns
        self.colmodel.append({
            'name': 'profit_margin',
            'label': 'Profit Margin',
            'formatter': 'percentage',
            'align': 'right',
            'sortable': False,
            'search': False,
            'width': 120
        })
        
        # Add action buttons column
        self.colmodel.append({
            'name': 'custom_actions',
            'label': 'Actions',
            'formatter': self.custom_actions_formatter,
            'sortable': False,
            'search': False,
            'width': 150,
            'fixed': True
        })
    
    def custom_actions_formatter(self, cellval, opts, rowObject):
        """Custom formatter for action buttons"""
        return f'''
            <button onclick="viewDetails({rowObject['id']})" class="btn btn-sm btn-info">
                <i class="fa fa-eye"></i>
            </button>
            <button onclick="printLabel({rowObject['id']})" class="btn btn-sm btn-secondary">
                <i class="fa fa-print"></i>
            </button>
        '''
```

### 2. Dynamic Configuration Based on User

Customize grid based on user permissions or preferences:

```python
class UserAwareProductViewSet(JqGridConfigMixin, viewsets.ModelViewSet):
    # ... basic configuration ...
    
    def get_visible_columns(self):
        """Dynamically determine visible columns based on user"""
        base_columns = ['id', 'name', 'category', 'price']
        
        if self.request.user.has_perm('products.view_cost'):
            base_columns.extend(['cost', 'profit_margin'])
        
        if self.request.user.is_staff:
            base_columns.extend(['supplier', 'last_updated', 'updated_by'])
        
        return base_columns
    
    def get_bulk_updateable_fields(self):
        """Limit bulk update fields based on permissions"""
        fields = ['category', 'in_stock']
        
        if self.request.user.has_perm('products.change_price'):
            fields.append('price')
        
        return fields
    
    def get_jqgrid_config(self, request):
        # Set dynamic attributes before building config
        self.visible_columns = self.get_visible_columns()
        self.bulk_updateable_fields = self.get_bulk_updateable_fields()
        
        return super().get_jqgrid_config(request)
```

### 3. Conditional Formatting and Row Highlighting

Add visual cues based on data:

```python
class VisualProductViewSet(JqGridConfigMixin, viewsets.ModelViewSet):
    # ... basic configuration ...
    
    # Conditional formatting for cells
    conditional_formatting = {
        'in_stock': [
            {
                'operator': 'eq',
                'value': False,
                'backgroundColor': '#ffcccc',
                'textColor': '#cc0000'
            }
        ],
        'price': [
            {
                'operator': 'lt',
                'value': 10,
                'backgroundColor': '#ccffcc',
                'textColor': '#006600'
            },
            {
                'operator': 'gt',
                'value': 100,
                'backgroundColor': '#ffffcc',
                'textColor': '#cc6600'
            }
        ]
    }
    
    # Row highlighting rules
    highlight_rules = [
        {
            'field': 'quantity',
            'operator': 'lt',
            'value': 5,
            'cssClass': 'low-stock-row'
        },
        {
            'field': 'discontinued',
            'operator': 'eq',
            'value': True,
            'cssClass': 'discontinued-row'
        }
    ]
```

## JavaScript Hooks and Extensions

### 1. Using JavaScript Hooks

Extend functionality using the built-in hook system. For complete hook documentation, see the [JavaScript Hooks Reference](JAVASCRIPT_HOOKS.md).

Quick example:

```javascript
// In your project's JavaScript file
$(document).ready(function() {
    // Hook: Before grid initialization
    window.jqGridConfig.hooks.beforeInitGrid = function(tableInstance) {
        console.log('Initializing grid:', tableInstance.tableName);
        
        // Add custom options
        tableInstance.options.customData = {
            department: 'electronics'
        };
    };
    
    // Hook: After grid initialization
    window.jqGridConfig.hooks.afterInitGrid = function(tableInstance, gridConfig) {
        // Add custom event handlers
        tableInstance.$grid.on('jqGridLoadComplete', function(event) {
            // Update statistics
            updateDashboardStats(tableInstance);
        });
    };
    
    // Hook: Before bulk update submission
    window.jqGridConfig.hooks.beforeSubmitBulkUpdate = function(tableInstance, ids, action, scope) {
        // Validate bulk update
        if (action.price && action.price < 0) {
            alert('Price cannot be negative!');
            return false; // Cancel the update
        }
        
        // Add confirmation for large updates
        if (scope === 'all' || ids.length > 100) {
            return confirm('This will update many records. Are you sure?');
        }
        
        return true; // Continue with update
    };
    
    // Hook: After bulk update completion
    window.jqGridConfig.hooks.afterSubmitBulkUpdate = function(tableInstance, ids, action, scope, response) {
        // Show custom notification
        showNotification('success', `Updated ${response.updated_count} records`);
        
        // Update related widgets
        refreshDashboard();
    };
});
```

### 2. Custom Notification System

Replace the default notification handler:

```javascript
// Custom notification using your preferred library
window.jqGridConfig.notify = function(type, message, tableInstance) {
    // Example using SweetAlert2
    if (window.Swal) {
        const config = {
            toast: true,
            position: 'top-end',
            showConfirmButton: false,
            timer: 3000,
            timerProgressBar: true
        };
        
        switch(type) {
            case 'success':
                Swal.fire({...config, icon: 'success', title: message});
                break;
            case 'error':
                Swal.fire({...config, icon: 'error', title: message, timer: 5000});
                break;
            case 'warning':
                Swal.fire({...config, icon: 'warning', title: message});
                break;
            default:
                Swal.fire({...config, icon: 'info', title: message});
        }
        return true;
    }
    
    // Fallback to console
    console.log(`[${type.toUpperCase()}]`, message);
    return false;
};
```

## Custom Field Types

### 1. Register Custom Field Configuration

Create custom field type handlers:

```python
# In your app's utils.py or a separate module
from django_jqgrid.mixins import JqGridConfigMixin

class ColorFieldConfig:
    """Custom configuration for color picker fields"""
    @staticmethod
    def get_config():
        return {
            'stype': 'text',
            'edittype': 'custom',
            'editoptions': {
                'custom_element': 'createColorPicker',
                'custom_value': 'getColorValue'
            },
            'formatter': 'colorFormatter',
            'unformat': 'colorUnformatter',
            'search_ops': ['eq', 'ne'],
            'sortable': True
        }

# Register in your ViewSet
class CustomFieldViewSet(JqGridConfigMixin, viewsets.ModelViewSet):
    def _apply_field_type_config(self, col_config, model_field, field_type):
        if field_type == 'ColorField':
            col_config.update(ColorFieldConfig.get_config())
        else:
            super()._apply_field_type_config(col_config, model_field, field_type)
```

### 2. JavaScript Implementation

Implement the custom field handlers:

```javascript
// Color picker implementation
window.createColorPicker = function(value, options) {
    const id = options.id || options.name;
    const html = `
        <div class="input-group">
            <input type="color" id="${id}" name="${options.name}" 
                   value="${value || '#000000'}" class="form-control">
            <span class="input-group-text color-preview" 
                  style="background-color: ${value || '#000000'}"></span>
        </div>
    `;
    return html;
};

window.getColorValue = function(elem, operation, value) {
    if (operation === 'get') {
        return $(elem).find('input[type="color"]').val();
    } else if (operation === 'set') {
        $(elem).find('input[type="color"]').val(value);
        $(elem).find('.color-preview').css('background-color', value);
    }
};

// Color formatter
$.fn.fmatter.colorFormatter = function(cellval, opts) {
    if (!cellval) return '';
    return `
        <div class="color-display" style="display: flex; align-items: center;">
            <span class="color-box" style="
                display: inline-block;
                width: 20px;
                height: 20px;
                background-color: ${cellval};
                border: 1px solid #ccc;
                margin-right: 8px;
            "></span>
            ${cellval}
        </div>
    `;
};
```

## Custom Bulk Actions

### 1. Register Custom Bulk Actions

Add custom bulk operations:

```python
class ProductViewSet(JqGridConfigMixin, JqGridBulkActionMixin, viewsets.ModelViewSet):
    # Define custom bulk actions
    bulk_actions = [
        {
            'id': 'apply-discount',
            'label': 'Apply Discount',
            'icon': 'fa-percent',
            'class': 'btn-warning'
        },
        {
            'id': 'generate-labels',
            'label': 'Generate Labels',
            'icon': 'fa-tag',
            'class': 'btn-info'
        },
        {
            'id': 'mark-featured',
            'label': 'Mark as Featured',
            'icon': 'fa-star',
            'class': 'btn-success'
        }
    ]
    
    @action(methods=['post'], detail=False)
    def bulk_action(self, request):
        """Extended bulk action handler"""
        action_id = request.data.get('action_id')
        
        # Handle custom actions
        if action_id == 'apply-discount':
            return self.apply_bulk_discount(request)
        elif action_id == 'generate-labels':
            return self.generate_bulk_labels(request)
        elif action_id == 'mark-featured':
            return self.mark_bulk_featured(request)
        
        # Fall back to default handler
        return super().bulk_action(request)
    
    def apply_bulk_discount(self, request):
        """Apply percentage discount to selected products"""
        ids = request.data.get('ids', [])
        discount_percent = request.data.get('discount_percent', 0)
        
        products = self.get_queryset().filter(id__in=ids)
        updated_count = 0
        
        for product in products:
            product.price = product.price * (1 - discount_percent / 100)
            product.save()
            updated_count += 1
        
        return Response({
            'status': 'success',
            'message': f'Applied {discount_percent}% discount to {updated_count} products'
        })
```

### 2. JavaScript Implementation

Handle custom bulk actions in JavaScript:

```javascript
// Extend bulk action handling
$(document).ready(function() {
    // Override or extend bulk action buttons
    window.jqGridConfig.bulkActions.tableActions.product = [
        {
            id: 'apply-discount',
            label: 'Apply Discount',
            icon: 'fa-percent',
            class: 'btn-warning',
            action: function(selectedIds, tableInstance) {
                // Show custom modal for discount input
                showDiscountModal(selectedIds, tableInstance);
            }
        },
        {
            id: 'generate-labels',
            label: 'Generate Labels',
            icon: 'fa-tag',
            class: 'btn-info',
            action: function(selectedIds, tableInstance) {
                // Generate PDF labels
                generateLabels(selectedIds, tableInstance);
            }
        }
    ];
});

function showDiscountModal(selectedIds, tableInstance) {
    // Create and show modal
    const modal = `
        <div class="modal fade" id="discountModal">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">Apply Discount</h5>
                    </div>
                    <div class="modal-body">
                        <div class="form-group">
                            <label>Discount Percentage:</label>
                            <input type="number" id="discountPercent" 
                                   class="form-control" min="0" max="100">
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-primary" 
                                onclick="applyDiscount('${selectedIds}', '${tableInstance.id}')">
                            Apply
                        </button>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    $('body').append(modal);
    $('#discountModal').modal('show');
}

function applyDiscount(selectedIds, tableId) {
    const discount = $('#discountPercent').val();
    const tableInstance = window.tables[tableId];
    
    $.ajax({
        url: `/api/${tableInstance.appName}/${tableInstance.tableName}/bulk_action/`,
        method: 'POST',
        data: JSON.stringify({
            ids: selectedIds.split(','),
            action_id: 'apply-discount',
            discount_percent: discount
        }),
        contentType: 'application/json',
        success: function(response) {
            $('#discountModal').modal('hide');
            tableInstance.$grid.trigger('reloadGrid');
            window.jqGridConfig.notify('success', response.message, tableInstance);
        }
    });
}
```

## Custom Formatters

### 1. Register Custom Formatters

Add specialized data formatters:

```javascript
// Register custom formatters
window.jqGridConfig.formatters = {
    // Status badge formatter
    statusBadge: function(cellval, opts) {
        const statusClasses = {
            'active': 'badge-success',
            'pending': 'badge-warning',
            'inactive': 'badge-danger',
            'archived': 'badge-secondary'
        };
        
        const badgeClass = statusClasses[cellval] || 'badge-info';
        return `<span class="badge ${badgeClass}">${cellval}</span>`;
    },
    
    // Progress bar formatter
    progressBar: function(cellval, opts) {
        const percentage = parseInt(cellval) || 0;
        const color = percentage < 30 ? 'danger' : 
                     percentage < 70 ? 'warning' : 'success';
        
        return `
            <div class="progress" style="height: 20px;">
                <div class="progress-bar bg-${color}" 
                     role="progressbar" 
                     style="width: ${percentage}%">
                    ${percentage}%
                </div>
            </div>
        `;
    },
    
    // Star rating formatter
    starRating: function(cellval, opts) {
        const rating = parseFloat(cellval) || 0;
        const fullStars = Math.floor(rating);
        const halfStar = rating % 1 >= 0.5 ? 1 : 0;
        const emptyStars = 5 - fullStars - halfStar;
        
        let html = '<span class="star-rating">';
        
        // Full stars
        for (let i = 0; i < fullStars; i++) {
            html += '<i class="fas fa-star text-warning"></i>';
        }
        
        // Half star
        if (halfStar) {
            html += '<i class="fas fa-star-half-alt text-warning"></i>';
        }
        
        // Empty stars
        for (let i = 0; i < emptyStars; i++) {
            html += '<i class="far fa-star text-warning"></i>';
        }
        
        html += ` (${rating.toFixed(1)})</span>`;
        return html;
    },
    
    // JSON viewer formatter
    jsonViewer: function(cellval, opts) {
        if (!cellval) return '';
        
        try {
            const data = typeof cellval === 'string' ? JSON.parse(cellval) : cellval;
            const jsonStr = JSON.stringify(data, null, 2);
            const id = `json_${opts.rowId}_${opts.colModel.name}`;
            
            return `
                <button class="btn btn-sm btn-info" 
                        onclick="showJsonModal('${id}', '${btoa(jsonStr)}')">
                    View JSON
                </button>
            `;
        } catch (e) {
            return '<span class="text-danger">Invalid JSON</span>';
        }
    }
};

// Helper function for JSON viewer
window.showJsonModal = function(id, encodedJson) {
    const json = atob(encodedJson);
    const modal = `
        <div class="modal fade" id="${id}_modal">
            <div class="modal-dialog modal-lg">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">JSON Viewer</h5>
                        <button type="button" class="close" data-dismiss="modal">
                            <span>&times;</span>
                        </button>
                    </div>
                    <div class="modal-body">
                        <pre class="json-viewer">${json}</pre>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    $('body').append(modal);
    $(`#${id}_modal`).modal('show').on('hidden.bs.modal', function() {
        $(this).remove();
    });
};
```

### 2. Using Custom Formatters

Apply formatters in your ViewSet:

```python
class ProductViewSet(JqGridConfigMixin, viewsets.ModelViewSet):
    jqgrid_field_overrides = {
        'status': {
            'formatter': 'statusBadge',
            'align': 'center',
            'width': 100
        },
        'completion_percentage': {
            'formatter': 'progressBar',
            'align': 'center',
            'width': 150
        },
        'rating': {
            'formatter': 'starRating',
            'align': 'center',
            'width': 150
        },
        'metadata': {
            'formatter': 'jsonViewer',
            'sortable': False,
            'search': False,
            'width': 100
        }
    }
```

## Custom Toolbar Buttons

### 1. Add Table-Specific Buttons

Register custom toolbar buttons:

```javascript
// Define custom buttons for specific tables
window.jqGridConfig.customButtons.product = [
    {
        id: 'import-csv',
        label: 'Import CSV',
        icon: 'fa-file-csv',
        class: 'btn-success',
        action: function(tableInstance) {
            showImportModal(tableInstance);
        }
    },
    {
        id: 'export-excel',
        label: 'Export Excel',
        icon: 'fa-file-excel',
        class: 'btn-primary',
        action: function(tableInstance) {
            exportToExcel(tableInstance);
        }
    },
    {
        id: 'print-report',
        label: 'Print Report',
        icon: 'fa-print',
        class: 'btn-secondary',
        action: function(tableInstance) {
            printReport(tableInstance);
        }
    }
];

// Implementation functions
function showImportModal(tableInstance) {
    const modal = `
        <div class="modal fade" id="importModal">
            <div class="modal-dialog">
                <div class="modal-content">
                    <form id="importForm" enctype="multipart/form-data">
                        <div class="modal-header">
                            <h5 class="modal-title">Import CSV</h5>
                        </div>
                        <div class="modal-body">
                            <div class="form-group">
                                <label>Select CSV File:</label>
                                <input type="file" name="csv_file" 
                                       accept=".csv" class="form-control" required>
                            </div>
                            <div class="form-check">
                                <input type="checkbox" name="update_existing" 
                                       class="form-check-input" id="updateExisting">
                                <label class="form-check-label" for="updateExisting">
                                    Update existing records
                                </label>
                            </div>
                        </div>
                        <div class="modal-footer">
                            <button type="submit" class="btn btn-primary">Import</button>
                            <button type="button" class="btn btn-secondary" 
                                    data-dismiss="modal">Cancel</button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    `;
    
    $('body').append(modal);
    $('#importModal').modal('show');
    
    $('#importForm').on('submit', function(e) {
        e.preventDefault();
        const formData = new FormData(this);
        
        $.ajax({
            url: `/api/${tableInstance.appName}/${tableInstance.tableName}/import_csv/`,
            method: 'POST',
            data: formData,
            processData: false,
            contentType: false,
            success: function(response) {
                $('#importModal').modal('hide');
                tableInstance.$grid.trigger('reloadGrid');
                window.jqGridConfig.notify('success', 
                    `Imported ${response.imported_count} records`, tableInstance);
            },
            error: function(xhr) {
                window.jqGridConfig.notify('error', 
                    'Import failed: ' + xhr.responseJSON.message, tableInstance);
            }
        });
    });
}

function exportToExcel(tableInstance) {
    // Get current filters
    const postData = tableInstance.$grid.jqGrid('getGridParam', 'postData');
    const queryString = $.param(postData);
    
    // Download Excel file
    window.location.href = 
        `/api/${tableInstance.appName}/${tableInstance.tableName}/export_excel/?${queryString}`;
}
```

### 2. Dynamic Button Visibility

Show/hide buttons based on conditions:

```javascript
window.jqGridConfig.hooks.afterCreateToolbar = function(tableInstance, toolbarId, gridConfig) {
    // Show import button only for users with permission
    if (!userHasPermission('can_import')) {
        $(`#${tableInstance.id}_import-csv`).hide();
    }
    
    // Show export button only if data exists
    const recordCount = tableInstance.$grid.jqGrid('getGridParam', 'records');
    if (recordCount === 0) {
        $(`#${tableInstance.id}_export-excel`).prop('disabled', true)
            .attr('title', 'No data to export');
    }
};
```

## Theme Customization

### 1. Custom CSS Variables

Create a custom theme:

```css
/* custom-jqgrid-theme.css */
:root {
    /* Grid colors */
    --jqgrid-header-bg: #2c3e50;
    --jqgrid-header-text: #ecf0f1;
    --jqgrid-row-bg: #ffffff;
    --jqgrid-row-alt-bg: #f8f9fa;
    --jqgrid-row-hover: #e3f2fd;
    --jqgrid-row-selected: #bbdefb;
    
    /* Border colors */
    --jqgrid-border: #dee2e6;
    --jqgrid-header-border: #34495e;
    
    /* Font settings */
    --jqgrid-font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    --jqgrid-font-size: 14px;
    
    /* Spacing */
    --jqgrid-cell-padding: 8px 12px;
}

/* Apply custom theme */
.ui-jqgrid {
    font-family: var(--jqgrid-font-family);
    font-size: var(--jqgrid-font-size);
}

.ui-jqgrid .ui-jqgrid-htable th {
    background-color: var(--jqgrid-header-bg);
    color: var(--jqgrid-header-text);
    border-color: var(--jqgrid-header-border);
    padding: var(--jqgrid-cell-padding);
}

.ui-jqgrid tr.jqgrow td {
    padding: var(--jqgrid-cell-padding);
    border-color: var(--jqgrid-border);
}

.ui-jqgrid tr.ui-row-ltr:nth-child(odd) {
    background-color: var(--jqgrid-row-alt-bg);
}

.ui-jqgrid tr.jqgrow:hover {
    background-color: var(--jqgrid-row-hover);
}

.ui-jqgrid tr.ui-state-highlight {
    background-color: var(--jqgrid-row-selected);
}

/* Custom status styles */
.low-stock-row {
    background-color: #fff3cd !important;
}

.discontinued-row {
    background-color: #f8d7da !important;
    opacity: 0.7;
}

/* Responsive improvements */
@media (max-width: 768px) {
    .ui-jqgrid {
        font-size: 12px;
    }
    
    .ui-jqgrid .ui-jqgrid-htable th,
    .ui-jqgrid tr.jqgrow td {
        padding: 4px 8px;
    }
}
```

### 2. Dark Mode Support

Implement dark mode theme:

```javascript
// Dark mode toggle
function toggleDarkMode(enabled) {
    if (enabled) {
        $('body').addClass('jqgrid-dark-mode');
        // Update grid theme
        $('.ui-jqgrid').each(function() {
            const gridId = $(this).attr('id').replace('gbox_', '');
            const tableInstance = window.tables[gridId];
            if (tableInstance) {
                tableInstance.$grid.jqGrid('setGridParam', {
                    styleUI: 'Bootstrap4',
                    iconSet: 'fontAwesome'
                });
            }
        });
    } else {
        $('body').removeClass('jqgrid-dark-mode');
    }
}

// Dark mode CSS
const darkModeStyles = `
    .jqgrid-dark-mode {
        --jqgrid-header-bg: #1a1a1a;
        --jqgrid-header-text: #e0e0e0;
        --jqgrid-row-bg: #2a2a2a;
        --jqgrid-row-alt-bg: #333333;
        --jqgrid-row-hover: #404040;
        --jqgrid-row-selected: #4a4a4a;
        --jqgrid-border: #555555;
    }
    
    .jqgrid-dark-mode .ui-jqgrid {
        color: #e0e0e0;
        background-color: #1a1a1a;
    }
    
    .jqgrid-dark-mode .ui-jqgrid .loading {
        background-color: rgba(0, 0, 0, 0.8);
        color: #e0e0e0;
    }
`;

// Inject dark mode styles
$('<style>').text(darkModeStyles).appendTo('head');
```

## Real-World Examples

### 1. E-commerce Product Grid

Complete example with all customizations:

```python
# models.py
class Product(models.Model):
    name = models.CharField(max_length=200)
    sku = models.CharField(max_length=50, unique=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField(default=0)
    status = models.CharField(max_length=20, choices=[
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('discontinued', 'Discontinued')
    ])
    featured = models.BooleanField(default=False)
    rating = models.DecimalField(max_digits=3, decimal_places=2, null=True)
    
    @property
    def profit_margin(self):
        if self.price and self.cost:
            return ((self.price - self.cost) / self.price) * 100
        return 0
    
    @property
    def in_stock(self):
        return self.quantity > 0

# serializers.py
class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    profit_margin = serializers.DecimalField(max_digits=5, decimal_places=2, read_only=True)
    in_stock = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Product
        fields = '__all__'

# views.py
class ProductViewSet(JqGridConfigMixin, JqGridBulkActionMixin, viewsets.ModelViewSet):
    queryset = Product.objects.select_related('category')
    serializer_class = ProductSerializer
    
    # Basic configuration
    visible_columns = [
        'id', 'sku', 'name', 'category', 'category_name', 
        'price', 'cost', 'profit_margin', 'quantity', 
        'in_stock', 'status', 'featured', 'rating'
    ]
    
    search_fields = ['name', 'sku', 'category__name']
    ordering_fields = ['name', 'price', 'quantity', 'created_at']
    ordering = ['-created_at']
    
    # Grouping configuration
    groupable_fields = ['category', 'status']
    aggregation_fields = {
        'price': ['min', 'max', 'avg'],
        'quantity': ['sum'],
        'profit_margin': ['avg']
    }
    
    # Frozen columns
    frozen_columns = ['id', 'sku', 'name']
    
    # Bulk update fields
    bulk_updateable_fields = ['category', 'price', 'status', 'featured']
    
    # Field overrides
    jqgrid_field_overrides = {
        'sku': {
            'width': 100,
            'fixed': True,
            'formatter': 'showlink',
            'formatoptions': {
                'baseLinkUrl': '/products/view/',
                'idName': 'id'
            }
        },
        'price': {
            'formatter': 'currency',
            'formatoptions': {'decimalPlaces': 2, 'prefix': '$'},
            'align': 'right',
            'width': 80
        },
        'cost': {
            'formatter': 'currency',
            'formatoptions': {'decimalPlaces': 2, 'prefix': '$'},
            'align': 'right',
            'width': 80,
            'hidden': True  # Hidden by default
        },
        'profit_margin': {
            'formatter': 'number',
            'formatoptions': {'decimalPlaces': 1, 'suffix': '%'},
            'align': 'right',
            'width': 100
        },
        'quantity': {
            'formatter': 'integer',
            'align': 'right',
            'width': 80
        },
        'in_stock': {
            'formatter': 'checkbox',
            'align': 'center',
            'width': 80
        },
        'status': {
            'formatter': 'statusBadge',
            'stype': 'select',
            'align': 'center',
            'width': 100
        },
        'featured': {
            'formatter': 'checkbox',
            'align': 'center',
            'width': 80
        },
        'rating': {
            'formatter': 'starRating',
            'align': 'center',
            'width': 150
        }
    }
    
    # Conditional formatting
    conditional_formatting = {
        'quantity': [
            {
                'operator': 'lt',
                'value': 5,
                'backgroundColor': '#ffcccc',
                'textColor': '#cc0000'
            },
            {
                'operator': 'eq',
                'value': 0,
                'backgroundColor': '#ff0000',
                'textColor': '#ffffff'
            }
        ],
        'profit_margin': [
            {
                'operator': 'lt',
                'value': 20,
                'backgroundColor': '#fff3cd',
                'textColor': '#856404'
            },
            {
                'operator': 'gt',
                'value': 50,
                'backgroundColor': '#d4edda',
                'textColor': '#155724'
            }
        ]
    }
    
    # Row highlighting
    highlight_rules = [
        {
            'field': 'status',
            'operator': 'eq',
            'value': 'discontinued',
            'cssClass': 'discontinued-row'
        },
        {
            'field': 'featured',
            'operator': 'eq',
            'value': True,
            'cssClass': 'featured-row'
        }
    ]
    
    # Custom actions
    @action(methods=['post'], detail=False)
    def import_csv(self, request):
        """Import products from CSV"""
        csv_file = request.FILES.get('csv_file')
        update_existing = request.data.get('update_existing', False)
        
        # Implementation...
        return Response({'imported_count': 100})
    
    @action(methods=['get'], detail=False)
    def export_excel(self, request):
        """Export filtered products to Excel"""
        # Apply filters from request
        queryset = self.filter_queryset(self.get_queryset())
        
        # Create Excel file
        # Implementation...
        return FileResponse(excel_file, as_attachment=True)
    
    def get_visible_columns(self):
        """Dynamic columns based on user permissions"""
        columns = super().get_visible_columns()
        
        # Hide cost and profit margin for non-staff users
        if not self.request.user.is_staff:
            columns = [c for c in columns if c not in ['cost', 'profit_margin']]
        
        return columns
```

### 2. Complete JavaScript Setup

```javascript
// product-grid.js
$(document).ready(function() {
    // Initialize product grid with all customizations
    const productGrid = window.initializeTableInstance('productGrid', 'products', 'product', {
        onInitComplete: function(tableInstance) {
            console.log('Product grid initialized');
            
            // Add keyboard shortcuts
            $(document).on('keydown', function(e) {
                if (e.ctrlKey && e.key === 'i') {
                    $('#import-csv').click();
                    e.preventDefault();
                }
            });
        },
        
        onGridComplete: function(tableInstance) {
            // Update statistics
            updateProductStats(tableInstance);
        },
        
        onSelectRow: function(rowid, status, e, tableInstance) {
            // Update detail panel
            if (status) {
                loadProductDetails(rowid);
            }
        },
        
        // Custom buttons
        customButtons: [
            {
                id: 'toggle-cost',
                label: 'Show Cost',
                icon: 'fa-eye',
                class: 'btn-info',
                action: function(tableInstance) {
                    const $btn = $(this);
                    const isHidden = tableInstance.$grid.jqGrid('getColProp', 'cost').hidden;
                    
                    if (isHidden) {
                        tableInstance.$grid.jqGrid('showCol', ['cost', 'profit_margin']);
                        $btn.html('<i class="fa fa-eye-slash"></i> Hide Cost');
                    } else {
                        tableInstance.$grid.jqGrid('hideCol', ['cost', 'profit_margin']);
                        $btn.html('<i class="fa fa-eye"></i> Show Cost');
                    }
                }
            },
            {
                id: 'quick-stats',
                label: 'Statistics',
                icon: 'fa-chart-bar',
                class: 'btn-primary',
                action: function(tableInstance) {
                    showProductStatistics(tableInstance);
                }
            }
        ]
    });
    
    // Additional initialization
    initializeProductFilters();
    initializeQuickSearch();
    setupAutoRefresh(30000); // Refresh every 30 seconds
});

// Helper functions
function updateProductStats(tableInstance) {
    const data = tableInstance.$grid.jqGrid('getRowData');
    
    let totalValue = 0;
    let outOfStock = 0;
    let featured = 0;
    
    data.forEach(row => {
        totalValue += parseFloat(row.price) * parseInt(row.quantity);
        if (parseInt(row.quantity) === 0) outOfStock++;
        if (row.featured === 'Yes') featured++;
    });
    
    $('#total-inventory-value').text('$' + totalValue.toFixed(2));
    $('#out-of-stock-count').text(outOfStock);
    $('#featured-count').text(featured);
}

function showProductStatistics(tableInstance) {
    // Get current filtered data
    const postData = tableInstance.$grid.jqGrid('getGridParam', 'postData');
    
    $.ajax({
        url: `/api/products/product/statistics/`,
        method: 'GET',
        data: postData,
        success: function(response) {
            // Show statistics in modal
            const modal = createStatisticsModal(response.data);
            $(modal).modal('show');
        }
    });
}
```

## Advanced Tips

### 1. Performance Optimization

```python
class OptimizedViewSet(JqGridConfigMixin, viewsets.ModelViewSet):
    def get_queryset(self):
        # Use select_related and prefetch_related
        queryset = super().get_queryset()
        return queryset.select_related(
            'category', 'supplier'
        ).prefetch_related(
            'tags', 'images'
        )
    
    def list(self, request, *args, **kwargs):
        # Cache commonly accessed data
        cache_key = f"grid_data_{request.user.id}_{request.GET.urlencode()}"
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return Response(cached_data)
        
        response = super().list(request, *args, **kwargs)
        cache.set(cache_key, response.data, 300)  # Cache for 5 minutes
        
        return response
```

### 2. Real-time Updates

```javascript
// WebSocket integration for real-time updates
function setupWebSocketUpdates(tableInstance) {
    const ws = new WebSocket(`ws://localhost:8000/ws/grid/${tableInstance.tableName}/`);
    
    ws.onmessage = function(event) {
        const data = JSON.parse(event.data);
        
        switch(data.action) {
            case 'update':
                // Update specific row
                tableInstance.$grid.jqGrid('setRowData', data.id, data.row);
                break;
            case 'delete':
                // Remove row
                tableInstance.$grid.jqGrid('delRowData', data.id);
                break;
            case 'insert':
                // Add new row
                tableInstance.$grid.jqGrid('addRowData', data.id, data.row, 'first');
                break;
            case 'refresh':
                // Refresh entire grid
                tableInstance.$grid.trigger('reloadGrid');
                break;
        }
    };
}
```

### 3. Custom Validation

```python
class ValidatedViewSet(JqGridConfigMixin, viewsets.ModelViewSet):
    def perform_create(self, serializer):
        # Custom validation before save
        if serializer.validated_data.get('price', 0) < 0:
            raise ValidationError({'price': 'Price cannot be negative'})
        
        # Additional business logic
        serializer.save(created_by=self.request.user)
    
    def perform_update(self, serializer):
        # Track changes
        instance = self.get_object()
        old_price = instance.price
        
        super().perform_update(serializer)
        
        # Log price changes
        if instance.price != old_price:
            PriceHistory.objects.create(
                product=instance,
                old_price=old_price,
                new_price=instance.price,
                changed_by=self.request.user
            )
```

## Troubleshooting

### Common Issues and Solutions

1. **Template tags not loading**
   - Ensure `django_jqgrid` is in INSTALLED_APPS
   - Restart Django server
   - Check for syntax errors in templates

2. **JavaScript customizations not working**
   - Verify script loading order
   - Check browser console for errors
   - Ensure jQuery is loaded before jqGrid

3. **Performance issues with large datasets**
   - Implement server-side pagination
   - Use database indexing
   - Enable query optimization
   - Consider caching strategies

4. **Custom formatters not displaying**
   - Register formatters before grid initialization
   - Check formatter function syntax
   - Verify formatter name matches configuration

## Conclusion

Django jqGrid is highly extensible and can be customized to meet virtually any requirement. By leveraging the hooks, overrides, and extension points described in this guide, you can create powerful, feature-rich data grids tailored to your specific needs.

For more examples and the latest updates, visit the [GitHub repository](https://github.com/yourusername/django-jqgrid).