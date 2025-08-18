# Django jqGrid JavaScript Hooks Reference

This document provides a complete reference for all available JavaScript hooks in django-jqgrid.

## Overview

Django jqGrid provides a comprehensive hook system that allows you to customize grid behavior without modifying the core code. Hooks are functions that are called at specific points during the grid lifecycle.

## Hook Registration

Hooks are registered on the global `window.jqGridConfig.hooks` object:

```javascript
window.jqGridConfig.hooks.hookName = function(...args) {
    // Your custom logic here
};
```

## Available Hooks

### 1. `beforeInitGrid`

Called before a grid is initialized.

**Parameters:**
- `tableInstance` - The table instance object

**Example:**
```javascript
window.jqGridConfig.hooks.beforeInitGrid = function(tableInstance) {
    console.log('Initializing grid:', tableInstance.tableName);
    
    // Modify options before grid creation
    tableInstance.options.rowNum = 100;
    tableInstance.options.customData = {
        department: getCurrentUserDepartment()
    };
};
```

### 2. `afterInitGrid`

Called after a grid has been initialized.

**Parameters:**
- `tableInstance` - The table instance object
- `gridConfig` - The grid configuration from server

**Example:**
```javascript
window.jqGridConfig.hooks.afterInitGrid = function(tableInstance, gridConfig) {
    // Add custom event handlers
    tableInstance.$grid.on('jqGridLoadComplete', function(event) {
        updateDashboardStats(tableInstance);
    });
    
    // Initialize custom features
    if (gridConfig.enable_realtime) {
        setupWebSocketUpdates(tableInstance);
    }
};
```

### 3. `beforeCreateToolbar`

Called before the toolbar is created.

**Parameters:**
- `tableInstance` - The table instance object
- `toolbarId` - The toolbar element ID
- `gridConfig` - The grid configuration

**Example:**
```javascript
window.jqGridConfig.hooks.beforeCreateToolbar = function(tableInstance, toolbarId, gridConfig) {
    // Add custom buttons based on table type
    if (tableInstance.tableName === 'orders') {
        if (!tableInstance.options.customButtons) {
            tableInstance.options.customButtons = [];
        }
        
        tableInstance.options.customButtons.push({
            id: 'process-orders',
            label: 'Process Orders',
            icon: 'fa-cogs',
            class: 'btn-primary',
            action: function() {
                processSelectedOrders(tableInstance);
            }
        });
    }
};
```

### 4. `afterCreateToolbar`

Called after the toolbar has been created.

**Parameters:**
- `tableInstance` - The table instance object
- `toolbarId` - The toolbar element ID
- `gridConfig` - The grid configuration

**Example:**
```javascript
window.jqGridConfig.hooks.afterCreateToolbar = function(tableInstance, toolbarId, gridConfig) {
    // Hide buttons based on permissions
    if (!userHasPermission('data_export')) {
        $(`#${tableInstance.id}_export-excel`).hide();
    }
    
    // Add tooltips
    $(`#${toolbarId} button`).tooltip({
        placement: 'top',
        trigger: 'hover'
    });
};
```

### 5. `beforeCreateBulkActions`

Called before bulk action buttons are created.

**Parameters:**
- `tableInstance` - The table instance object
- `bulkActionConfig` - The bulk action configuration

**Example:**
```javascript
window.jqGridConfig.hooks.beforeCreateBulkActions = function(tableInstance, bulkActionConfig) {
    // Add table-specific bulk actions
    if (tableInstance.tableName === 'products') {
        bulkActionConfig.actions.push({
            id: 'calculate-tax',
            label: 'Calculate Tax',
            icon: 'fa-calculator',
            class: 'btn-info'
        });
    }
    
    // Remove actions based on permissions
    if (!userHasPermission('bulk_delete')) {
        bulkActionConfig.actions = bulkActionConfig.actions.filter(
            action => action.id !== 'bulk-delete'
        );
    }
};
```

### 6. `afterCreateBulkActions`

Called after bulk action buttons have been created.

**Parameters:**
- `tableInstance` - The table instance object
- `bulkActionConfig` - The bulk action configuration

**Example:**
```javascript
window.jqGridConfig.hooks.afterCreateBulkActions = function(tableInstance, bulkActionConfig) {
    // Add custom handlers to bulk action buttons
    $(`#${tableInstance.id}_calculate-tax`).on('click', function() {
        calculateTaxForSelected(tableInstance);
    });
};
```

### 7. `beforeSubmitBulkUpdate`

Called before a bulk update is submitted. Can be used to validate or cancel the update.

**Parameters:**
- `tableInstance` - The table instance object
- `ids` - Array of selected record IDs
- `action` - The action object containing field updates
- `scope` - 'specific' or 'all'

**Returns:**
- `true` to continue with the update
- `false` to cancel the update

**Example:**
```javascript
window.jqGridConfig.hooks.beforeSubmitBulkUpdate = function(tableInstance, ids, action, scope) {
    // Validate price updates
    if (action.price !== undefined && action.price < 0) {
        alert('Price cannot be negative!');
        return false;
    }
    
    // Confirm large updates
    if (scope === 'all' || ids.length > 100) {
        return confirm(`This will update ${scope === 'all' ? 'ALL' : ids.length} records. Continue?`);
    }
    
    // Log updates for audit
    console.log('Bulk update:', {
        table: tableInstance.tableName,
        user: getCurrentUser(),
        ids: ids,
        changes: action
    });
    
    return true;
};
```

### 8. `afterSubmitBulkUpdate`

Called after a bulk update has been completed.

**Parameters:**
- `tableInstance` - The table instance object
- `ids` - Array of updated record IDs
- `action` - The action object containing field updates
- `scope` - 'specific' or 'all'
- `response` - The server response

**Example:**
```javascript
window.jqGridConfig.hooks.afterSubmitBulkUpdate = function(tableInstance, ids, action, scope, response) {
    // Show custom notification
    if (window.showNotification) {
        showNotification('success', 
            `Successfully updated ${response.updated_count || ids.length} records`
        );
    }
    
    // Update related widgets
    if (typeof updateDashboard === 'function') {
        updateDashboard();
    }
    
    // Track analytics
    if (window.gtag) {
        gtag('event', 'bulk_update', {
            'event_category': 'data_management',
            'event_label': tableInstance.tableName,
            'value': ids.length
        });
    }
};
```

## Global Configuration Hooks

Besides lifecycle hooks, you can also override global configuration functions:

### `window.jqGridConfig.notify`

Override the default notification handler.

**Parameters:**
- `type` - Notification type: 'success', 'error', 'warning', 'info'
- `message` - The message to display
- `tableInstance` - The table instance (optional)

**Returns:**
- `true` if notification was handled
- `false` to use fallback notification

**Example:**
```javascript
window.jqGridConfig.notify = function(type, message, tableInstance) {
    // Use a custom notification library
    if (window.Swal) {
        Swal.fire({
            toast: true,
            position: 'top-end',
            icon: type === 'error' ? 'error' : type,
            title: message,
            showConfirmButton: false,
            timer: 3000
        });
        return true;
    }
    
    // Fallback to console
    console.log(`[${type.toUpperCase()}]`, message);
    return false;
};
```

### `window.jqGridConfig.timeSince`

Override the time formatting function.

**Parameters:**
- `date` - Date string or Date object

**Returns:**
- Formatted time string

**Example:**
```javascript
window.jqGridConfig.timeSince = function(date) {
    // Use moment.js if available
    if (window.moment) {
        return moment(date).fromNow();
    }
    
    // Custom implementation
    const seconds = Math.floor((new Date() - new Date(date)) / 1000);
    if (seconds < 60) return 'just now';
    if (seconds < 3600) return Math.floor(seconds / 60) + ' minutes ago';
    if (seconds < 86400) return Math.floor(seconds / 3600) + ' hours ago';
    return Math.floor(seconds / 86400) + ' days ago';
};
```

## Advanced Hook Patterns

### 1. Conditional Hook Registration

```javascript
// Register hooks based on user role
if (currentUser.role === 'admin') {
    window.jqGridConfig.hooks.beforeInitGrid = function(tableInstance) {
        // Admin-specific configuration
        tableInstance.options.showHiddenColumns = true;
    };
}
```

### 2. Hook Chaining

```javascript
// Save original hook
const originalBeforeInit = window.jqGridConfig.hooks.beforeInitGrid;

// Add new functionality while preserving existing
window.jqGridConfig.hooks.beforeInitGrid = function(tableInstance) {
    // Call original hook if it exists
    if (typeof originalBeforeInit === 'function') {
        originalBeforeInit(tableInstance);
    }
    
    // Add new functionality
    console.log('Grid init:', tableInstance.tableName);
};
```

### 3. Async Hooks

```javascript
window.jqGridConfig.hooks.afterInitGrid = async function(tableInstance, gridConfig) {
    // Fetch user preferences
    try {
        const prefs = await fetchUserPreferences(tableInstance.tableName);
        
        // Apply preferences
        if (prefs.hiddenColumns) {
            prefs.hiddenColumns.forEach(col => {
                tableInstance.$grid.jqGrid('hideCol', col);
            });
        }
    } catch (error) {
        console.error('Failed to load preferences:', error);
    }
};
```

### 4. Event-Driven Hooks

```javascript
// Trigger custom events from hooks
window.jqGridConfig.hooks.afterSubmitBulkUpdate = function(tableInstance, ids, action, scope, response) {
    // Trigger custom event
    $(document).trigger('jqgrid:bulkUpdate', {
        table: tableInstance.tableName,
        ids: ids,
        action: action,
        response: response
    });
};

// Listen for custom events elsewhere
$(document).on('jqgrid:bulkUpdate', function(event, data) {
    console.log('Bulk update completed:', data);
    refreshRelatedComponents(data.table);
});
```

## Best Practices

1. **Check for Dependencies**: Always verify that required functions/libraries exist before using them
2. **Error Handling**: Wrap hook code in try-catch blocks to prevent breaking the grid
3. **Performance**: Keep hooks lightweight - defer heavy operations
4. **Documentation**: Comment your hooks to explain their purpose
5. **Namespace**: Use a consistent naming pattern for custom functions

## Example: Complete Hook Setup

```javascript
// hooks.js - Complete hook configuration for a project
(function() {
    'use strict';
    
    // Initialize hooks object if not exists
    window.jqGridConfig = window.jqGridConfig || {};
    window.jqGridConfig.hooks = window.jqGridConfig.hooks || {};
    
    // Configuration
    const config = {
        enableLogging: true,
        enableAnalytics: true,
        customButtons: {
            products: ['import', 'export', 'barcode'],
            orders: ['process', 'invoice', 'ship']
        }
    };
    
    // Utility functions
    const log = function(message, data) {
        if (config.enableLogging) {
            console.log(`[jqGrid] ${message}`, data || '');
        }
    };
    
    // Register all hooks
    window.jqGridConfig.hooks.beforeInitGrid = function(tableInstance) {
        log('Initializing grid', tableInstance.tableName);
        
        // Add performance monitoring
        tableInstance.initStartTime = performance.now();
        
        // Set user preferences
        const savedPrefs = localStorage.getItem(`grid_prefs_${tableInstance.tableName}`);
        if (savedPrefs) {
            const prefs = JSON.parse(savedPrefs);
            Object.assign(tableInstance.options, prefs);
        }
    };
    
    window.jqGridConfig.hooks.afterInitGrid = function(tableInstance, gridConfig) {
        const loadTime = performance.now() - tableInstance.initStartTime;
        log(`Grid initialized in ${loadTime.toFixed(2)}ms`, tableInstance.tableName);
        
        // Track analytics
        if (config.enableAnalytics && window.gtag) {
            gtag('event', 'grid_load', {
                'event_category': 'performance',
                'event_label': tableInstance.tableName,
                'value': Math.round(loadTime)
            });
        }
        
        // Setup auto-save preferences
        tableInstance.$grid.on('jqGridColumnChooser', function() {
            const colModel = tableInstance.$grid.jqGrid('getGridParam', 'colModel');
            const hiddenCols = colModel
                .filter(col => col.hidden)
                .map(col => col.name);
            
            localStorage.setItem(`grid_prefs_${tableInstance.tableName}`, 
                JSON.stringify({ hiddenColumns: hiddenCols })
            );
        });
    };
    
    window.jqGridConfig.hooks.beforeCreateToolbar = function(tableInstance, toolbarId, gridConfig) {
        // Add table-specific buttons
        const buttons = config.customButtons[tableInstance.tableName];
        if (buttons && buttons.length) {
            log('Adding custom buttons', buttons);
            
            if (!tableInstance.options.customButtons) {
                tableInstance.options.customButtons = [];
            }
            
            buttons.forEach(buttonType => {
                tableInstance.options.customButtons.push(
                    createButtonConfig(buttonType, tableInstance)
                );
            });
        }
    };
    
    window.jqGridConfig.hooks.beforeSubmitBulkUpdate = function(tableInstance, ids, action, scope) {
        log('Bulk update validation', { ids: ids.length, action, scope });
        
        // Validate based on table
        switch(tableInstance.tableName) {
            case 'products':
                if (action.price && action.price < action.cost) {
                    alert('Price cannot be less than cost!');
                    return false;
                }
                break;
                
            case 'orders':
                if (action.status === 'shipped' && !confirm('Mark orders as shipped?')) {
                    return false;
                }
                break;
        }
        
        return true;
    };
    
    window.jqGridConfig.hooks.afterSubmitBulkUpdate = function(tableInstance, ids, action, scope, response) {
        log('Bulk update completed', response);
        
        // Refresh dependent components
        $(document).trigger('dataChanged', {
            source: 'jqGrid',
            table: tableInstance.tableName,
            action: 'bulkUpdate',
            affectedIds: ids
        });
    };
    
    // Helper function to create button configurations
    function createButtonConfig(buttonType, tableInstance) {
        const buttonConfigs = {
            'import': {
                id: 'import-data',
                label: 'Import',
                icon: 'fa-upload',
                class: 'btn-success',
                action: () => showImportDialog(tableInstance)
            },
            'export': {
                id: 'export-data',
                label: 'Export',
                icon: 'fa-download',
                class: 'btn-primary',
                action: () => exportTableData(tableInstance)
            },
            'barcode': {
                id: 'print-barcode',
                label: 'Print Barcodes',
                icon: 'fa-barcode',
                class: 'btn-info',
                action: () => printBarcodes(tableInstance)
            },
            'process': {
                id: 'process-orders',
                label: 'Process',
                icon: 'fa-cogs',
                class: 'btn-warning',
                action: () => processOrders(tableInstance)
            },
            'invoice': {
                id: 'generate-invoice',
                label: 'Invoice',
                icon: 'fa-file-invoice',
                class: 'btn-info',
                action: () => generateInvoices(tableInstance)
            },
            'ship': {
                id: 'ship-orders',
                label: 'Ship',
                icon: 'fa-truck',
                class: 'btn-success',
                action: () => shipOrders(tableInstance)
            }
        };
        
        return buttonConfigs[buttonType] || null;
    }
    
    // Initialize notification system
    window.jqGridConfig.notify = function(type, message, tableInstance) {
        // Try multiple notification systems in order of preference
        
        // 1. Try toastr
        if (window.toastr) {
            toastr[type](message);
            return true;
        }
        
        // 2. Try SweetAlert2
        if (window.Swal) {
            Swal.fire({
                toast: true,
                position: 'top-end',
                icon: type,
                title: message,
                showConfirmButton: false,
                timer: 3000
            });
            return true;
        }
        
        // 3. Try Bootstrap toast
        if ($.fn.toast) {
            $('<div class="toast" role="alert">')
                .addClass(`bg-${type}`)
                .html(`
                    <div class="toast-header">
                        <strong class="mr-auto">${type.toUpperCase()}</strong>
                        <button type="button" class="ml-2 mb-1 close" data-dismiss="toast">
                            <span>&times;</span>
                        </button>
                    </div>
                    <div class="toast-body">${message}</div>
                `)
                .toast({ delay: 3000 })
                .toast('show');
            return true;
        }
        
        // 4. Fallback to console
        console.log(`[${type.toUpperCase()}]`, message);
        return false;
    };
    
    log('jqGrid hooks initialized');
})();
```

## Debugging Hooks

To debug hook execution, you can enable logging:

```javascript
// Enable hook debugging
window.jqGridConfig.debugHooks = true;

// Wrap hooks with logging
const wrapHook = (hookName, hookFn) => {
    return function(...args) {
        if (window.jqGridConfig.debugHooks) {
            console.group(`Hook: ${hookName}`);
            console.log('Arguments:', args);
            console.time('Execution time');
        }
        
        const result = hookFn.apply(this, args);
        
        if (window.jqGridConfig.debugHooks) {
            console.log('Result:', result);
            console.timeEnd('Execution time');
            console.groupEnd();
        }
        
        return result;
    };
};

// Apply debugging to all hooks
Object.keys(window.jqGridConfig.hooks).forEach(hookName => {
    const originalHook = window.jqGridConfig.hooks[hookName];
    if (typeof originalHook === 'function') {
        window.jqGridConfig.hooks[hookName] = wrapHook(hookName, originalHook);
    }
});
```

## Conclusion

The hook system in django-jqgrid provides powerful extension points that allow you to customize virtually every aspect of grid behavior without modifying the core code. By using these hooks effectively, you can create highly customized grid implementations that meet your specific requirements while maintaining upgradeability.