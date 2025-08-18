/**
 * Django jqGrid Configuration
 * Separated and configurable grid initialization and utilities.
 */

// Configuration object for jqGrid
var JqGridConfig = {
    // Default formatters that can be extended by users
    formatters: {
        // Boolean formatter - displays Yes/No instead of true/false
        booleanFormatter: function(cellvalue, options, rowObject) {
            return cellvalue ? 'Yes' : 'No';
        },
        
        // Date formatter - formats date as YYYY-MM-DD
        dateFormatter: function(cellvalue, options, rowObject) {
            if (!cellvalue) return '';
            var date = new Date(cellvalue);
            return date.getFullYear() + '-' + 
                   ('0' + (date.getMonth() + 1)).slice(-2) + '-' + 
                   ('0' + date.getDate()).slice(-2);
        },
        
        // DateTime formatter - formats date as YYYY-MM-DD HH:MM
        datetimeFormatter: function(cellvalue, options, rowObject) {
            if (!cellvalue) return '';
            var date = new Date(cellvalue);
            return date.getFullYear() + '-' + 
                   ('0' + (date.getMonth() + 1)).slice(-2) + '-' + 
                   ('0' + date.getDate()).slice(-2) + ' ' +
                   ('0' + date.getHours()).slice(-2) + ':' +
                   ('0' + date.getMinutes()).slice(-2);
        },
        
        // Currency formatter - formats number as currency
        currencyFormatter: function(cellvalue, options, rowObject) {
            if (cellvalue === null || cellvalue === undefined) return '';
            return parseFloat(cellvalue).toFixed(2).replace(/\d(?=(\d{3})+\.)/g, '$&,');
        },
        
        // Link formatter - creates a clickable link
        linkFormatter: function(cellvalue, options, rowObject) {
            if (!cellvalue) return '';
            return '<a href="' + cellvalue + '" target="_blank">' + 
                   cellvalue.split('/').pop() + '</a>';
        },
        
        // Email formatter - creates a mailto link
        emailFormatter: function(cellvalue, options, rowObject) {
            if (!cellvalue) return '';
            return '<a href="mailto:' + cellvalue + '">' + cellvalue + '</a>';
        },
        
        // Status formatter - displays a colored status indicator
        statusFormatter: function(cellvalue, options, rowObject) {
            var statusClasses = {
                'active': 'success',
                'pending': 'warning',
                'inactive': 'danger',
                'completed': 'info'
            };
            
            var statusClass = statusClasses[cellvalue?.toLowerCase()] || 'secondary';
            return '<span class="badge badge-' + statusClass + '">' + 
                   cellvalue + '</span>';
        },
        
        // Button formatter - creates an open button for IDs
        openButtonFormatter: function(cellvalue, options, rowObject) {
            if(!cellvalue) return '';
            return `<a role='button' onclick="openFormCard({id:'${cellvalue}'})" type="button" class="btn btn-info">Open</a>`;
        },
        
        // Image formatter - displays an image
        imageFormatter: function(cellvalue, options, rowObject) {
            if(!cellvalue) return '';
            return `<img src="${cellvalue}" alt="Image" class="img-thumbnail" style="max-width: 100px; max-height: 60px;" />`;
        },
        
        // File formatter - creates a download link
        fileFormatter: function(cellvalue, options, rowObject) {
            if(!cellvalue) return '';
            return `<a href="${cellvalue}" class="btn btn-info" download>Download</a>`;
        }
    },
    
    // Default button configurations that can be extended by users
    defaultButtons: {
        refresh: {
            id: 'refreshGrid',
            label: 'Refresh',
            icon: 'fa-sync-alt',
            class: 'btn-outline-primary',
            action: function(tableInstance) {
                tableInstance.$grid.trigger('reloadGrid');
            }
        },
        clearFilters: {
            id: 'clearFilters',
            label: 'Clear Filters',
            icon: 'fa-filter',
            class: 'btn-outline-secondary',
            action: function(tableInstance) {
                tableInstance.$grid.jqGrid('setGridParam', { search: false, postData: { filters: "" } }).trigger('reloadGrid');
            }
        },
        saveFilter: {
            id: 'saveFilters',
            label: 'Save Filter',
            icon: 'fa-save',
            class: 'btn-outline-warning',
            action: function(tableInstance) {
                // Implemented in grid initialization
            }
        },
        deleteFilter: {
            id: 'deleteFilters',
            label: 'Delete Filter',
            icon: 'fa-trash',
            class: 'btn-outline-danger',
            action: function(tableInstance) {
                // Implemented in grid initialization
            }
        },
    },
    
    // Default bulk actions that can be extended by users
    defaultBulkActions: {
        update: {
            id: 'bulk-update',
            label: 'Update Selected',
            icon: 'fa-edit',
            class: 'btn-primary',
            action: function(tableInstance) {
                showBulkUpdateModal(tableInstance);
            }
        },
        delete: {
            id: 'bulk-delete',
            label: 'Delete Selected',
            icon: 'fa-trash',
            class: 'btn-danger',
            action: function(tableInstance) {
                performBulkDelete(tableInstance);
            }
        }
    },
    
    // Extension point for user-defined formatters
    customFormatters: {},
    
    // Extension point for user-defined buttons
    customButtons: {},
    
    // Extension point for user-defined bulk actions
    customBulkActions: {},
    
    // Initialize formatters
    initFormatters: function() {
        // Register all formatters with jqGrid
        for (var key in this.formatters) {
            if (this.formatters.hasOwnProperty(key)) {
                $.fn.fmatter[key.replace('Formatter', '')] = this.formatters[key];
            }
        }
        
        // Register custom formatters
        for (var key in this.customFormatters) {
            if (this.customFormatters.hasOwnProperty(key)) {
                $.fn.fmatter[key] = this.customFormatters[key];
            }
        }
    },
    
    // Get all available buttons (default + custom)
    getAllButtons: function() {
        return Object.assign({}, this.defaultButtons, this.customButtons);
    },
    
    // Get all available bulk actions (default + custom)
    getAllBulkActions: function() {
        return Object.assign({}, this.defaultBulkActions, this.customBulkActions);
    },
    
    // Method to extend with custom formatters
    extendFormatters: function(newFormatters) {
        this.customFormatters = Object.assign({}, this.customFormatters, newFormatters);
        this.initFormatters();
    },
    
    // Method to extend with custom buttons
    extendButtons: function(newButtons) {
        this.customButtons = Object.assign({}, this.customButtons, newButtons);
    },
    
    // Method to extend with custom bulk actions
    extendBulkActions: function(newBulkActions) {
        this.customBulkActions = Object.assign({}, this.customBulkActions, newBulkActions);
    }
};

// Initialize formatters when the script loads
JqGridConfig.initFormatters();

// Common utility functions for use with jqGrid
var JqGridUtils = {
    
    // Apply conditional formatting to grid cells
    applyConditionalFormatting: function(tableInstance, conditions) {
        var grid = tableInstance.$grid;
        var rows = grid.jqGrid('getDataIDs');
        
        rows.forEach(function(rowId) {
            var rowData = grid.jqGrid('getRowData', rowId);
            
            // Check conditions for each cell
            for (var field in conditions) {
                if (conditions.hasOwnProperty(field) && rowData[field] !== undefined) {
                    var value = rowData[field];
                    var rules = conditions[field];
                    
                    // Apply each rule that matches
                    rules.forEach(function(rule) {
                        if (JqGridUtils.evaluateCondition(value, rule.operator, rule.value)) {
                            grid.jqGrid('setCell', rowId, field, '', {
                                color: rule.textColor || '',
                                background: rule.backgroundColor || ''
                            });
                        }
                    });
                }
            }
        });
    },
    
    // Evaluate a condition for conditional formatting
    evaluateCondition: function(cellValue, operator, targetValue) {
        switch(operator) {
            case 'eq': return cellValue == targetValue;
            case 'ne': return cellValue != targetValue;
            case 'lt': return parseFloat(cellValue) < parseFloat(targetValue);
            case 'le': return parseFloat(cellValue) <= parseFloat(targetValue);
            case 'gt': return parseFloat(cellValue) > parseFloat(targetValue);
            case 'ge': return parseFloat(cellValue) >= parseFloat(targetValue);
            case 'contains': return String(cellValue).indexOf(targetValue) >= 0;
            case 'startswith': return String(cellValue).startsWith(targetValue);
            case 'endswith': return String(cellValue).endsWith(targetValue);
            default: return false;
        }
    },
    
    // Create a Select2 dropdown for a field
    initializeSelect2ForField: function($select, dataUrl) {
        if (!dataUrl) return;
        
        // Destroy existing Select2 if it exists
        if ($select.data('select2')) {
            $select.select2('destroy');
        }
        
        // Initialize Select2 with AJAX data source
        $select.select2({
            theme: 'bootstrap4',
            width: '100%',
            placeholder: $select.data('placeholder') || '-- Select --',
            allowClear: true,
            ajax: {
                url: dataUrl,
                dataType: 'json',
                delay: 250,
                data: function(params) {
                    return {
                        search: params.term,
                        page: params.page || 1
                    };
                },
                processResults: function(response, params) {
                    params.page = params.page || 1;
                    
                    // Process response data
                    var items = [];
                    if (response && response.data && response.data.data) {
                        items = response.data.data.map(function(item) {
                            return {
                                id: item.id,
                                text: item.text,
                                selected: item.selected || false
                            };
                        });
                    }
                    
                    return {
                        results: items,
                        pagination: {
                            more: (params.page * 30) < (response.data.recordsTotal || 0)
                        }
                    };
                },
                cache: true
            },
            minimumInputLength: 0
        });
        
        // Mark as initialized
        $select.attr('data-select2-initialized', 'true');
    }
};

// Format date/time since a given date (utility function)
function timeSince(date) {
    const seconds = Math.floor((new Date() - new Date(date)) / 1000);
    const intervals = {
        year: 31536000,
        month: 2592000,
        day: 86400,
        hour: 3600,
        minute: 60,
        second: 1
    };
    for (const [unit, value] of Object.entries(intervals)) {
        const count = Math.floor(seconds / value);
        if (count >= 1) {
            return `${count} ${unit}${count > 1 ? 's' : ''} ago`;
        }
    }
    return "Just now";
}

// Make JqGridConfig and JqGridUtils available globally
window.JqGridConfig = JqGridConfig;
window.JqGridUtils = JqGridUtils;