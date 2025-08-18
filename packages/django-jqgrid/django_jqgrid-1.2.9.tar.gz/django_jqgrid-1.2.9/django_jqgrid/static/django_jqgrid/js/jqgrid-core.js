/**
 * Enhanced Multi-Database jqGrid Manager
 * Handles multiple jqGrid instances on a single page with isolated states and user customization
 */

// Global namespace for managing multiple tables
window.tables = window.tables || {};

/**
 * Configuration for global settings
 * Can be customized by users
 */
window.jqGridConfig = window.jqGridConfig || {
    // Default notification handler - can be overridden by user
    notify: function(type, message, tableInstance) {
        // If toastr is available, use it
        if (window.toastr && typeof window.toastr[type] === 'function') {
            window.toastr[type](message);
            return true;
        }
        
        // Default implementation uses alert for simplicity
        if (type === 'error') {
            alert('Error: ' + message);
        } else if (type === 'warning') {
            alert('Warning: ' + message);
        } else {
            alert(message);
        }
        
        return false;
    },

    // Default time formatter - can be overridden by user
    timeSince: function(date) {
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
    },

    // Custom formatters - can be extended by user
    formatters: {},

    // Custom row renderers - can be defined by user
    rowRenderers: {

    },

    // Custom toolbar buttons - can be added by user
    customButtons: {},

    // Default grid options - can be overridden
    defaultGridOptions: {},

    // Hooks for extending functionality
    hooks: {
        beforeInitGrid: null,
        afterInitGrid: null,
        beforeCreateToolbar: null,
        afterCreateToolbar: null,
        beforeCreateBulkActions: null,
        afterCreateBulkActions: null,
        beforeSubmitBulkUpdate: null,
        afterSubmitBulkUpdate: null
    }
};

/**
 * Initialize formatters
 */
function initFormatters() {
    if (!$.fn.fmatter) return;

    // Base formatters
    const baseFormatters = {
        mobile: function(cellval, opts) {
            if(!$.fmatter.isEmpty(cellval)) {
                return `<a href="tel:${cellval}">${cellval}</a>`;
            }
            return $.fn.fmatter.defaultFormat(cellval, opts);
        },

        open_button: function(cellval, opts) {
            if(!$.fmatter.isEmpty(cellval)) {
                return `<a role='button' onclick="openFormCard({id:'${cellval}'})" type="button" class="btn btn-info">Open</a>`;
            }
            return $.fn.fmatter.defaultFormat(cellval, opts);
        },

        image: function(cellval, opts) {
            if(!$.fmatter.isEmpty(cellval)) {
                return `<img src="${cellval}" />`;
            }
            return $.fn.fmatter.defaultFormat(cellval, opts);
        },

        file: function(cellval, opts) {
            if(!$.fmatter.isEmpty(cellval)) {
                return `<a href="${cellval}" class="btn btn-info" download>Download</a>`;
            }
            return $.fn.fmatter.defaultFormat(cellval, opts);
        },

        datetimeLocal: function(cellval, opts, rowdata) {
            if ($.fmatter.isEmpty(cellval)) {
                return "";
            }

            // Convert string to Date object
            let dateObj = new Date(cellval);
            if (isNaN(dateObj.getTime())) {
                return cellval; // Return original value if invalid
            }

            // Format date to YYYY-MM-DDTHH:MM
            let year = dateObj.getFullYear();
            let month = String(dateObj.getMonth() + 1).padStart(2, '0');
            let day = String(dateObj.getDate()).padStart(2, '0');
            let hours = String(dateObj.getHours()).padStart(2, '0');
            let minutes = String(dateObj.getMinutes()).padStart(2, '0');

            return `${year}-${month}-${day}T${hours}:${minutes}`;
        }
    };

    // Unformatter for datetime fields
    $.fn.fmatter.datetimeLocalUnformat = function(cellval, opts, cell) {
        // For editing, we need to return a proper ISO string
        if (cellval) {
            // If the value is already in ISO format or datepicker format, parse it
            let dateObj = new Date(cellval);
            if (!isNaN(dateObj.getTime())) {
                return dateObj.toISOString(); // Return ISO string for backend
            }
        }
        return cellval;
    };

    // Register base formatters
    for (const [name, formatter] of Object.entries(baseFormatters)) {
        $.fn.fmatter[name] = formatter;
    }

    // Register custom formatters
    for (const [name, formatter] of Object.entries(window.jqGridConfig.formatters)) {
        $.fn.fmatter[name] = formatter;
    }
}

/**
 * Helper utilities
 */
const utils = {
    // Show notification message
    notify: function(type, message, tableInstance) {
        // Call the user-configurable notification handler
        return window.jqGridConfig.notify(type, message, tableInstance);
    },
    
    // Format time since a given date
    timeSince: function(date) {
        return window.jqGridConfig.timeSince(date);
    },
    
    // Check if an object is empty
    isEmpty: function(obj) {
        if (obj === null || obj === undefined) return true;
        if (typeof obj === 'string') return obj.trim().length === 0;
        if (Array.isArray(obj)) return obj.length === 0;
        if (typeof obj === 'object') return Object.keys(obj).length === 0;
        return false;
    },
    
    // Safe JSON parse with error handling
    safeJsonParse: function(str) {
        try {
            return JSON.parse(str);
        } catch (e) {
            console.error('JSON Parse Error:', e);
            return null;
        }
    }
};

/**
 * Initialize a table instance with its own isolated state
 * @param {string} tableId - DOM ID of the table
 * @param {string} appName - Application name for the table
 * @param {string} tableName - Database table name
 * @param {Object} options - Additional options for configuration
 */
window.initializeTableInstance = function(tableId, appName, tableName, options = {}) {
    // Initialize formatters
    initFormatters();

    // Create table instance if it doesn't exist
    if (!window.tables[tableId]) {
        window.tables[tableId] = {
            id: tableId,
            appName: appName,
            tableName: tableName,
            options: options,
            $grid: null,
            bulkActions: {},
            toolbarSettings: {},
            headerTitles: {},
            selectionIds: []
        };
    }

    // Reference to this table instance
    const tableInstance = window.tables[tableId];

    // Set grid and pager selectors
    tableInstance.gridSelector = `#${tableId}`;
    tableInstance.pagerSelector = options.pagerSelector || `#${tableId}Pager`;
    tableInstance.toppagerSelector = options.toppagerSelector || `#${tableId}_toppager`;
    tableInstance.toolbarSelector = options.toolbarSelector || `#${tableId}_toolbar`;

    // Allow user to apply hooks before grid initialization
    if (typeof window.jqGridConfig.hooks.beforeInitGrid === 'function') {
        window.jqGridConfig.hooks.beforeInitGrid(tableInstance);
    }

    // Initialize grid
    return initializeGridForTable(tableInstance);
};

/**
 * Helper function to construct API URL for a table instance
 * @param {Object} tableInstance - Table instance configuration
 * @param {string} endpoint - Optional endpoint to append (e.g., 'bulk_action', 'jqgrid_config')
 * @returns {string} The constructed API URL
 */
function getApiUrl(tableInstance, endpoint = '') {
    let baseUrl;
    if (tableInstance.options.baseUrl) {
        baseUrl = tableInstance.options.baseUrl;
    } else {
        // Default URL construction - assumes pluralized app name and table name
        // Handle special case where app URL might differ from app name
        let appPath = tableInstance.appName;
        
        // If appName is 'example', use 'examples' in the URL
        if (appPath === 'example') {
            appPath = 'examples';
        } else if (!appPath.endsWith('s')) {
            appPath = appPath + 's';
        }
        
        const tableName = tableInstance.tableName.endsWith('s') ? tableInstance.tableName : tableInstance.tableName + 's';
        baseUrl = `/${appPath}/api/${tableName}/`;
    }
    return endpoint ? `${baseUrl}${endpoint}/` : baseUrl;
}

/**
 * Initialize jqGrid for a specific table instance
 * @param {Object} tableInstance - Table instance configuration
 */
function initializeGridForTable(tableInstance) {
    const gridUrl = getApiUrl(tableInstance);

    // Store reference to the jQuery grid object
    tableInstance.$grid = $(tableInstance.gridSelector);

    // Fetch grid configuration from the server
    return $.ajax({
        url: getApiUrl(tableInstance, 'jqgrid_config'),
        method: 'GET',
        dataType: 'json',
        success: function(response) {
            if (!response || !response.data) {
                utils.notify('error', 'Invalid grid configuration received from server.', tableInstance);
                return;
            }

            const gridConfig = response.data;

            // Set grid title if present in config
            if (gridConfig.jqgrid_options.caption) {
                $(`${tableInstance.toolbarSelector} .card-title`).text(gridConfig.jqgrid_options.caption);
            }

            // Modify grid configuration for this instance
            const gridOptions = gridConfig.jqgrid_options;
            gridOptions.pager = tableInstance.pagerSelector;

            // Add instance-specific event handlers
            gridOptions.gridComplete = function() {
                // Custom event handler logic
                if (typeof tableInstance.options.onGridComplete === 'function') {
                    tableInstance.options.onGridComplete(tableInstance);
                }
            };

            // Handle row selection events - store selected IDs in this instance
            gridOptions.onSelectRow = function(rowid, status, e) {
                updateInstanceSelection(tableInstance);
                if (typeof tableInstance.options.onSelectRow === 'function') {
                    tableInstance.options.onSelectRow(rowid, status, e, tableInstance);
                }
            };

            gridOptions.onSelectAll = function(aRowids, status) {
                updateInstanceSelection(tableInstance);
                if (typeof tableInstance.options.onSelectAll === 'function') {
                    tableInstance.options.onSelectAll(aRowids, status, tableInstance);
                }
            };

            // Process dynamic dropdowns in colModel
            gridOptions.colModel.forEach(function(item) {
                // Handle search options with data URLs
                if (item.searchoptions && item.searchoptions.dataUrl) {
                    item.searchoptions['buildSelect'] = function(data) {
                        try {
                            data = utils.safeJsonParse(data);
                            if (!data || !data.data || !data.data.data) {
                                return '<select><option value="">Error loading options</option></select>';
                            }
                            
                            var options = '<select><option value="">Select</option>';
                            $.each(data.data.data, function(index, item) {
                                selected = item.selected ? 'selected' : '';
                                options += '<option value="' + item.id + '" ' + selected + '>' + item.text + '</option>';
                            });
                            options += '</select>';
                            return options;
                        } catch (e) {
                            console.error('Error building search select:', e);
                            return '<select><option value="">Error loading options</option></select>';
                        }
                    };
                }

                // Handle edit options with data URLs
                if (item.editoptions && item.editoptions.dataUrl) {
                    item.editoptions['dataUrl'] = function(data) {
                        // Dynamically build the URL with the current row ID
                        if (data != '_empty') {
                            return item.editoptions['dataUrlTemp'].replace('<id>', data);
                        } else {
                            return item.editoptions['dataUrlTemp'].replace('<id>/', '').replace('dropdown_pk', 'dropdown');
                        }
                    };

                    item.editoptions['buildSelect'] = function(data) {
                        try {
                            data = utils.safeJsonParse(data);
                            if (!data || !data.data || !data.data.data) {
                                return '<select><option value="">Error loading options</option></select>';
                            }
                            
                            var options = '<select><option value="">Select</option>';
                            $.each(data.data.data, function(index, item) {
                                selected = item.selected ? 'selected="selected"' : '';
                                options += '<option value="' + item.id + '" ' + selected + '>' + item.text + '</option>';
                            });
                            options += '</select>';
                            return options;
                        } catch (e) {
                            console.error('Error building edit select:', e);
                            return '<select><option value="">Error loading options</option></select>';
                        }
                    };
                }
            });

            // Check if custom row renderer is defined for this table
            let rowRendering = false;
            
            // First check for a custom renderer in the jqGridConfig
            let customRenderer = window.jqGridConfig.rowRenderers[tableInstance.id];
            
            if (customRenderer) {
                rowRendering = true;
                // Configure grid for custom row rendering
                gridOptions.colModel = [{
                    "label": tableInstance.id,
                    "name": tableInstance.id,
                    "formatter": customRenderer,
                    "frozen": true,
                    "formatoptions": {
                        "keys": true
                    }
                }];

                gridOptions.colNames = [tableInstance.id.toUpperCase()];
                gridOptions.shrinkToFit = true;
                gridOptions.multiselect = false;
                gridOptions.colMenu = false;
                gridOptions.toolbar = false;
                gridOptions.sortable = false;
                gridOptions.menubar = false;
                gridOptions.headertitles = false;
                gridOptions.rownumbers = false;

                // Special configuration for contact list
                if (tableInstance.id === 'lead_contacts_jqGrid') {
                    gridOptions.scroll = 1;
                    gridOptions.scrollrows = true;
                    gridOptions.scrollOffset = 0;
                    gridOptions.scrollTimeout = 100;
                }
            }

            // Merge with default grid options (allowing users to set global defaults)
            const mergedOptions = $.extend(true, {}, window.jqGridConfig.defaultGridOptions, gridOptions);

            // Initialize the grid
            tableInstance.$grid.jqGrid(mergedOptions);

            if (rowRendering) {
                return;
            }

            // Apply method options
            if (gridConfig.method_options) {
                // Setup navGrid for this instance
                if (gridConfig.method_options.navGrid) {
                    const navOpts = gridConfig.method_options.navGrid;
                    tableInstance['searchOptions'] = navOpts.searchOptions;
                    tableInstance.$grid.jqGrid('navGrid', tableInstance.pagerSelector,
                        navOpts.options,
                        navOpts.editOptions,
                        navOpts.addOptions,
                        navOpts.delOptions,
                        navOpts.searchOptions,
                        navOpts.viewOptions
                    );
                }

                // Setup filterToolbar for this instance
                if (gridConfig.method_options.filterToolbar) {
                    tableInstance.$grid.jqGrid('filterToolbar', gridConfig.method_options.filterToolbar.options);
                }

                // Other method options
                if (gridConfig.method_options.setGroupHeaders) {
                    tableInstance.$grid.jqGrid('setGroupHeaders', gridConfig.method_options.setGroupHeaders.options);
                }

                if (gridConfig.method_options.setFrozenColumns &&
                    gridConfig.method_options.setFrozenColumns.enabled) {
                    tableInstance.$grid.jqGrid('setFrozenColumns');
                }
            }

            // Initialize toolbar with instance-specific settings
            initializeToolbarForTable(tableInstance, gridConfig);

            // Initialize bulk actions with instance-specific settings
            if (gridConfig.bulk_action_config) {
                initializeBulkActionsForTable(tableInstance, gridConfig.bulk_action_config);
            }

            // Fetch additional data for this table
            fetchAdditionalDataForTable(tableInstance);
            

            // Trigger custom event when grid is initialized
            if (typeof tableInstance.options.onInitComplete === 'function') {
                tableInstance.options.onInitComplete(tableInstance);
            }

            // Allow user to apply hooks after grid initialization
            if (typeof window.jqGridConfig.hooks.afterInitGrid === 'function') {
                window.jqGridConfig.hooks.afterInitGrid(tableInstance, gridConfig);
            }
        },
        error: function(xhr, status, error) {
            utils.notify('error', 'Error loading grid configuration: ' + error, tableInstance);
            console.error('AJAX Error:', xhr.responseText);
        }
    });
}

/**
 * Initialize toolbar for a specific table instance
 * @param {Object} tableInstance - Table instance configuration
 * @param {Object} gridConfig - Grid configuration from server
 */
function initializeToolbarForTable(tableInstance, gridConfig) {
    // Create toolbar ID specific to this table
    const toolbarId = tableInstance.id + '_toolbar';

    // Allow user to apply hooks before toolbar creation
    if (typeof window.jqGridConfig.hooks.beforeCreateToolbar === 'function') {
        window.jqGridConfig.hooks.beforeCreateToolbar(tableInstance, toolbarId, gridConfig);
    }

    // Create toolbar if it doesn't exist
    let toolbarContainer = document.getElementById(toolbarId);

    if (!toolbarContainer) {
        toolbarContainer = document.createElement('div');
        toolbarContainer.id = toolbarId;
        toolbarContainer.className = 'jqgrid-toolbar card-header';

        // Create toolbar content with instance-specific IDs
        toolbarContainer.innerHTML = `
            <div class="d-flex justify-content-between align-items-center">
                <div class="toolbar-left d-flex align-items-center">
                    <h3 class="card-title mr-3" id="${tableInstance.id}_title">Data Grid</h3>
                    <div class="btn-group toolbar-actions mr-2">
                        <button type="button" data-table="${tableInstance.id}" id="${tableInstance.id}_refreshGrid" class="btn btn-outline-primary btn-sm">
                            <i class="fas fa-sync-alt"></i> Refresh
                        </button>
                        <button type="button" data-table="${tableInstance.id}" id="${tableInstance.id}_clearFilters" class="btn btn-outline-secondary btn-sm">
                            <i class="fas fa-filter"></i> Clear Filters
                        </button>
                        <button type="button" data-table="${tableInstance.id}" id="${tableInstance.id}_saveFilters" class="btn btn-outline-warning btn-sm">
                            <i class="fas fa-filter"></i> Save Filter
                        </button>
                        <button type="button" data-table="${tableInstance.id}" id="${tableInstance.id}_deleteFilters" class="btn btn-outline-danger btn-sm">
                            <i class="fas fa-filter"></i> Delete Filter
                        </button>
                    </div>
                </div>
                <div class="toolbar-right d-flex align-items-center">
                    <div id="${tableInstance.id}_custom_buttons" class="btn-group mr-2"></div>
                    <div id="${tableInstance.id}_bulk_action_buttons" class="btn-group" style="display: none;">
                        <!-- Bulk action buttons will be added here -->
                    </div>
                </div>
            </div>
            <div id="${tableInstance.id}_bulk_selection_info" class="mt-2" style="display: none;">
                <input type='radio' name='${tableInstance.id}_bulk_selection_choice' class="form-check-input" id='${tableInstance.id}_bulk_selection_choice-specific' value="specific" checked><span class="badge badge-info">
                    <i class="fas fa-check-square"></i> <label for='${tableInstance.id}_bulk_selection_choice-specific'><span id="${tableInstance.id}_selected_count">0</span> items selected
                    </span>
                </label>
                <input type='radio' name='${tableInstance.id}_bulk_selection_choice' class="form-check-input" id='${tableInstance.id}_bulk_selection_choice-all' value="all"><span class="badge badge-info">
                    <i class="fas fa-check-square"></i> <label for='${tableInstance.id}_bulk_selection_choice-all'>All items selected</label>
                </span>
                <button type="button" id="${tableInstance.id}_clear_selection" class="btn btn-sm btn-link">
                    Clear selection
                </button>
            </div>
            <div id="${tableInstance.id}_gridMessages" class="alert alert-dismissible mt-2" style="display: none;"></div>
        `;

        // Add toolbar to DOM before the grid
        const $toppager = $(tableInstance.toppagerSelector);
        if ($toppager.length) {
            $toppager.before(toolbarContainer);
        } else {
            tableInstance.$grid.before(toolbarContainer);
        }
    }

    // Store toolbar settings in table instance
    tableInstance.toolbarSettings = {
        toolbarId: toolbarId,
        refreshButtonId: `${tableInstance.id}_refreshGrid`,
        clearFiltersButtonId: `${tableInstance.id}_clearFilters`,
        saveFiltersButtonId: `${tableInstance.id}_saveFilters`,
        deleteFiltersButtonId: `${tableInstance.id}_deleteFilters`,
        bulkActionsContainerId: `${tableInstance.id}_bulk_action_buttons`,
        selectionInfoId: `${tableInstance.id}_bulk_selection_info`,
        selectedCountId: `${tableInstance.id}_selected_count`,
        clearSelectionButtonId: `${tableInstance.id}_clear_selection`,
        customButtonsContainerId: `${tableInstance.id}_custom_buttons`,
        messageContainerId: `${tableInstance.id}_gridMessages`
    };

    // Add event handlers for toolbar buttons
    $(`#${tableInstance.toolbarSettings.refreshButtonId}`).on('click', function() {
        tableInstance.$grid.trigger('reloadGrid');
    });

    $(`#${tableInstance.toolbarSettings.clearFiltersButtonId}`).on('click', function() {
        // Clear the grid parameters
        tableInstance.$grid.jqGrid('setGridParam', { search: false, postData: { filters: "" } });
        
        // Clear the filter toolbar inputs if it exists
        if (tableInstance.$grid[0].clearToolbar) {
            tableInstance.$grid[0].clearToolbar.call(tableInstance.$grid[0], false);
        }
        
        // Reload the grid
        tableInstance.$grid.trigger('reloadGrid');
    });

    $(`#${tableInstance.toolbarSettings.saveFiltersButtonId}`).on('click', function() {
        const name = prompt("Filter Name");
        const value = tableInstance.$grid.jqGrid('getGridParam', 'postData')['filters'];

        if (!name || !value) return;

        $.ajax({
            url: `/api/grid/filters/`,
            success: function(data) {
                if (!data || !data.data || !data.data.data || !data.data.data[0]) {
                    utils.notify('error', 'Content type data not found', tableInstance);
                    return;
                }
                
                const table = data.data.data[0].id;

                $.ajax({
                    url: `/api/django_jqgrid/grid-filter/`,
                    contentType: 'application/json',
                    method: 'POST',
                    data: JSON.stringify({
                        "name": name,
                        "key": "tmplFilters",
                        "table": table,
                        "value": value
                    }),
                    // CSRF token is handled by $.ajaxSetup in jqgrid-csrf.js
                    success: function(data) {
                        utils.notify('success', 'Filter saved successfully', tableInstance);
                    },
                    error: function(xhr, status, error) {
                        utils.notify('error', 'Error saving filter: ' + error, tableInstance);
                    }
                });
            },
            error: function(xhr, status, error) {
                utils.notify('error', 'Error getting content type: ' + error, tableInstance);
            }
        });
    });

    $(`#${tableInstance.toolbarSettings.deleteFiltersButtonId}`).on('click', function() {
        const filterParam = tableInstance.$grid.jqGrid('getGridParam', 'postData').filters;

        if (!tableInstance['searchOptions'] ||
            !tableInstance['searchOptions']['tmplFilters'] ||
            !tableInstance['searchOptions']['tmplIds']) {
            utils.notify('warning', 'No saved filters found', tableInstance);
            return;
        }

        let filterDeleted = false;
        
        tableInstance['searchOptions']['tmplFilters'].forEach(function(item, index) {
            if (item === filterParam) {
                const filterId = tableInstance['searchOptions']['tmplIds'][index];
                
                filterDeleted = true;

                $.ajax({
                    url: `/api/django_jqgrid/grid-filter/${filterId}/`,
                    contentType: 'application/json',
                    method: 'DELETE',
                    // CSRF token is handled by $.ajaxSetup in jqgrid-csrf.js
                    success: function(data) {
                        utils.notify('success', 'Filter deleted successfully', tableInstance);
                        initializeGridForTable(tableInstance);
                    },
                    error: function(xhr, status, error) {
                        utils.notify('error', 'Error deleting filter: ' + error, tableInstance);
                    }
                });
            }
        });
        
        if (!filterDeleted) {
            utils.notify('warning', 'No matching filter found to delete', tableInstance);
        }
    });

    $(`#${tableInstance.toolbarSettings.clearSelectionButtonId}`).on('click', function() {
        tableInstance.$grid.jqGrid('resetSelection');
        updateInstanceSelection(tableInstance);
    });

    // Add custom buttons
    addCustomButtonsToToolbar(tableInstance);

    // Allow user to apply hooks after toolbar creation
    if (typeof window.jqGridConfig.hooks.afterCreateToolbar === 'function') {
        window.jqGridConfig.hooks.afterCreateToolbar(tableInstance, toolbarId, gridConfig);
    }
}

/**
 * Add custom buttons to the toolbar
 * @param {Object} tableInstance - Table instance configuration
 */
/**
 * Add custom buttons to the toolbar
 * @param {Object} tableInstance - Table instance configuration
 */
function addCustomButtonsToToolbar(tableInstance) {
    // Get custom buttons container
    const buttonContainer = document.getElementById(tableInstance.toolbarSettings.customButtonsContainerId);
    if (!buttonContainer) return;

    // Clear existing buttons
    buttonContainer.innerHTML = '';

    // Add instance-specific custom buttons if any
    if (tableInstance.options.customButtons && tableInstance.options.customButtons.length > 0) {
        tableInstance.options.customButtons.forEach(button => {
            const btn = document.createElement('button');
            btn.type = 'button';
            btn.id = button.id || `${tableInstance.id}_custom_btn_${Math.random().toString(36).substring(2, 9)}`;
            btn.className = `btn ${button.class || 'btn-secondary'} btn-sm`;
            btn.innerHTML = `<i class="fas ${button.icon}"></i> ${button.label}`;

            // Use closure to preserve tableInstance reference
            btn.addEventListener('click', function() {
                if (typeof button.action === 'function') {
                    button.action(tableInstance);
                }
            });

            buttonContainer.appendChild(btn);
        });
    }

    // Add global custom buttons for this table type if any
    const globalButtons = window.jqGridConfig.customButtons[tableInstance.tableName] || [];
    globalButtons.forEach(button => {
        // Skip if button is already added from instance options
        if (tableInstance.options.customButtons &&
            tableInstance.options.customButtons.some(b => b.id === button.id)) {
            return;
        }

        const btn = document.createElement('button');
        btn.type = 'button';
        btn.id = button.id || `${tableInstance.id}_global_btn_${Math.random().toString(36).substring(2, 9)}`;
        btn.className = `btn ${button.class || 'btn-secondary'} btn-sm`;
        btn.innerHTML = `<i class="fas ${button.icon}"></i> ${button.label}`;

        // Use closure to preserve tableInstance reference
        btn.addEventListener('click', function() {
            if (typeof button.action === 'function') {
                button.action(tableInstance);
            }
        });

        buttonContainer.appendChild(btn);
    });
}

/**
 * Initialize bulk actions for a specific table instance
 * @param {Object} tableInstance - Table instance configuration
 * @param {Object} bulkActionConfig - Bulk action configuration from server
 */
function initializeBulkActionsForTable(tableInstance, bulkActionConfig) {
    // Allow user to apply hooks before creating bulk actions
    if (typeof window.jqGridConfig.hooks.beforeCreateBulkActions === 'function') {
        window.jqGridConfig.hooks.beforeCreateBulkActions(tableInstance, bulkActionConfig);
    }
    
    // Store bulk action config in table instance
    tableInstance.bulkActions = bulkActionConfig;

    // Get container for bulk action buttons
    const buttonContainer = document.getElementById(tableInstance.toolbarSettings.bulkActionsContainerId);
    if (!buttonContainer) return;

    // Clear existing buttons
    buttonContainer.innerHTML = '';

    // Add buttons for each action
    if (bulkActionConfig.actions && Array.isArray(bulkActionConfig.actions)) {
        bulkActionConfig.actions.forEach(action => {
            const button = document.createElement('button');
            button.type = 'button';
            button.id = `${tableInstance.id}_${action.id}`;
            button.className = `btn ${action.class || 'btn-secondary'} btn-sm`;
            button.innerHTML = `<i class="fas ${action.icon}"></i> ${action.label}`;

            // Use closure to preserve tableInstance reference
            button.addEventListener('click', function() {
                const selectedIds = tableInstance.$grid.jqGrid('getGridParam', 'selarrrow');
                if (selectedIds && selectedIds.length > 0) {
                    if (action.id === 'bulk-update') {
                        showBulkUpdateModal(tableInstance);
                    } else if (action.id === 'bulk-delete') {
                        performBulkDelete(tableInstance);
                    } else if (typeof action.action === 'function') {
                        // Call action with tableInstance as context
                        action.action(selectedIds, tableInstance);
                    }
                } else {
                    utils.notify('warning', 'Please select at least one row', tableInstance);
                }
            });

            buttonContainer.appendChild(button);
        });
    }

    // Create bulk update modal for this instance if it doesn't exist
    createBulkUpdateModal(tableInstance);
    
    // Allow user to apply hooks after creating bulk actions
    if (typeof window.jqGridConfig.hooks.afterCreateBulkActions === 'function') {
        window.jqGridConfig.hooks.afterCreateBulkActions(tableInstance, bulkActionConfig);
    }
}

/**
 * Create modal for bulk updates specific to a table instance
 * @param {Object} tableInstance - Table instance configuration
 */
function createBulkUpdateModal(tableInstance) {
    // Check if modal already exists
    const modalId = `${tableInstance.id}_bulk_update_modal`;
    if (document.getElementById(modalId)) {
        return;
    }

    // Create modal element
    const modal = document.createElement('div');
    modal.className = 'modal fade';
    modal.id = modalId;
    modal.setAttribute('tabindex', '-1');
    modal.setAttribute('role', 'dialog');
    modal.setAttribute('aria-labelledby', `${modalId}_title`);
    modal.setAttribute('aria-hidden', 'true');

    // Set modal content
    modal.innerHTML = `
        <div class="modal-dialog modal-lg">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title" id="${modalId}_title">
                        Bulk Update <span id="${modalId}_item_count"></span>
                    </h5>
                    <button type="button" class="close" data-dismiss="modal" aria-label="Close">
                        <span aria-hidden="true">&times;</span>
                    </button>
                </div>
                <div class="modal-body">
                    <div class="alert alert-info">
                        <i class="fas fa-info-circle"></i>
                        Select fields to update. Only checked fields will be modified.
                    </div>
                    <form id="${modalId}_form">
                        <div id="${modalId}_fields_container" class="row">
                            <!-- Fields will be added dynamically -->
                        </div>
                    </form>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-dismiss="modal">Cancel</button>
                    <button type="button" class="btn btn-primary" id="${modalId}_submit">
                        Update Selected Items
                    </button>
                </div>
            </div>
        </div>
    `;

    // Add to document
    document.body.appendChild(modal);

    // Store modal settings in table instance
    tableInstance.bulkUpdateModal = {
        modalId: modalId,
        formId: `${modalId}_form`,
        fieldsContainerId: `${modalId}_fields_container`,
        itemCountId: `${modalId}_item_count`,
        submitButtonId: `${modalId}_submit`
    };

    // Add submit handler
    const submitButton = document.getElementById(tableInstance.bulkUpdateModal.submitButtonId);
    if (submitButton) {
        submitButton.addEventListener('click', function() {
            submitBulkUpdate(tableInstance);
        });
    }

    // Add modal hidden event to clean up Select2
    $(`#${modalId}`).on('hidden.bs.modal', function() {
        // Destroy all Select2 instances to prevent memory leaks
        if (typeof $.fn.select2 !== 'undefined') {
            try {
                $(this).find('.select2-hidden-accessible').select2('destroy');
            } catch (e) {
                // Ignore errors
            }
        }
    });
}

/**
 * Show bulk update modal with fields from selected records
 * @param {Object} tableInstance - Table instance configuration
 */
function showBulkUpdateModal(tableInstance) {
    // Get selected IDs
    const selectedIds = tableInstance.$grid.jqGrid('getGridParam', 'selarrrow');
    if (!selectedIds || selectedIds.length === 0) {
        utils.notify('warning', 'Please select at least one row', tableInstance);
        return;
    }

    // Update selected count in modal
    const countElement = document.getElementById(tableInstance.bulkUpdateModal.itemCountId);
    if (countElement) {
        countElement.textContent = `(${selectedIds.length} items)`;
    }

    // Get fields container
    const fieldsContainer = document.getElementById(tableInstance.bulkUpdateModal.fieldsContainerId);
    if (!fieldsContainer) return;

    // Clear previous fields
    fieldsContainer.innerHTML = '';

    // Get updatable field names from bulk action config
    let updateableFieldNames = [];

    if (tableInstance.bulkActions && tableInstance.bulkActions.updateableFields) {
        updateableFieldNames = tableInstance.bulkActions.updateableFields;
    }

    if (!updateableFieldNames.length) return;

    // Get column model to extract field configurations
    const colModel = tableInstance.$grid.jqGrid('getGridParam', 'colModel');

    // Create mapping of field names to column configurations
    const fieldConfigs = {};
    colModel.forEach(col => {
        if (col.name) {
            fieldConfigs[col.name] = col;
        }
    });

    // Add fields for each updateable field
    updateableFieldNames.forEach(fieldName => {
        // Get field configuration from column model
        const colConfig = fieldConfigs[fieldName];

        // Skip if field not found in colModel
        if (!colConfig) return;

        const fieldDiv = document.createElement('div');
        fieldDiv.className = 'col-md-6 mb-3';

        let fieldHtml = '';
        let fieldType = 'text';
        let hasDataUrl = false;
        let dataUrl = '';

        // Check if field has dataUrl for select options
        if (colConfig.editoptions && colConfig.editoptions.dataUrlTemp) {
            hasDataUrl = true;
            // Generate the data URL - replace <id> placeholder with ''
            dataUrl = colConfig.editoptions.dataUrlTemp.replace('<id>/', '').replace('dropdown_pk', 'dropdown');
        }

        // Determine field type based on formatter or stype
        if (colConfig.formatter === 'checkbox' || colConfig.edittype === 'checkbox') {
            fieldType = 'checkbox';
            fieldHtml = `
                <div class="custom-control custom-checkbox">
                    <input type="checkbox" class="custom-control-input" id="${tableInstance.id}_bulk_field_value_${fieldName}" name="${fieldName}-value">
                    <label class="custom-control-label" for="${tableInstance.id}_bulk_field_value_${fieldName}">Yes</label>
                </div>
            `;
        } else if (colConfig.formatter === 'select' || colConfig.edittype === 'select') {
            fieldType = 'select';

            if (hasDataUrl) {
                // Create a select element for Select2 with data URL
                fieldHtml = `
                    <select class="form-control select2-ajax select2-dropdown"
                            id="${tableInstance.id}_bulk_field_value_${fieldName}"
                            name="${fieldName}-value"
                            data-url="${dataUrl}"
                            data-placeholder="-- Select --">
                        <option value="">-- Select --</option>
                    </select>
                `;
            } else if (colConfig.editoptions && colConfig.editoptions.value) {
                // Parse select options from string like "value1:text1;value2:text2"
                const optionsMap = {};
                colConfig.editoptions.value.split(';').forEach(option => {
                    const [value, text] = option.split(':');
                    if (value && text) {
                        optionsMap[value] = text;
                    }
                });

                options = Object.entries(optionsMap).map(([value, text]) =>
                    `<option value="${value}">${text}</option>`
                ).join('');

                fieldHtml = `
                    <select class="form-control" id="${tableInstance.id}_bulk_field_value_${fieldName}" name="${fieldName}-value">
                        <option value="">-- Select --</option>
                        ${options}
                    </select>
                `;
            } else {
                fieldHtml = `
                    <select class="form-control" id="${tableInstance.id}_bulk_field_value_${fieldName}" name="${fieldName}-value">
                        <option value="">-- Select --</option>
                    </select>
                `;
            }
        } else if (colConfig.formatter === 'date' || colConfig.stype === 'date') {
            fieldType = 'date';
            fieldHtml = `
                <input type="date" class="form-control" id="${tableInstance.id}_bulk_field_value_${fieldName}" name="${fieldName}-value">
            `;
        } else if (colConfig.formatter === 'integer' || colConfig.formatter === 'number' ||
                  colConfig.stype === 'integer' || colConfig.stype === 'number') {
            fieldType = 'number';
            fieldHtml = `
                <input type="number" class="form-control" id="${tableInstance.id}_bulk_field_value_${fieldName}" name="${fieldName}-value">
            `;
        } else if (colConfig.formatter === 'datetime-local' || colConfig.stype === 'datetime-local') {
            fieldType = 'datetime-local';
            fieldHtml = `
                <input type="datetime-local" class="form-control" id="${tableInstance.id}_bulk_field_value_${fieldName}" name="${fieldName}-value">
            `;
        } else {
            // Default to text input
            fieldHtml = `
                <input type="text" class="form-control" id="${tableInstance.id}_bulk_field_value_${fieldName}" name="${fieldName}-value">
            `;
        }

        // Complete field HTML with label and enable checkbox
        fieldDiv.innerHTML = `
            <div class="form-group">
                <div class="custom-control custom-checkbox mb-1">
                    <input type="checkbox" class="custom-control-input" id="${tableInstance.id}_bulk_field_${fieldName}" name="${fieldName}-enabled">
                    <label class="custom-control-label" for="${tableInstance.id}_bulk_field_${fieldName}">
                        <strong>${colConfig.label || fieldName}</strong>
                    </label>
                </div>
                ${fieldHtml}
            </div>
        `;

        // Add field to container
        fieldsContainer.appendChild(fieldDiv);

        // Add event handler to toggle input state based on checkbox
        const enableCheckbox = fieldDiv.querySelector(`#${tableInstance.id}_bulk_field_${fieldName}`);
        const valueInput = fieldDiv.querySelector(`#${tableInstance.id}_bulk_field_value_${fieldName}`);

        if (enableCheckbox && valueInput) {
            enableCheckbox.addEventListener('change', function() {
                valueInput.disabled = !this.checked;

                // If using Select2 and the field is enabled, initialize or refresh it
                if (this.checked && hasDataUrl && $(valueInput).hasClass('select2-dropdown')) {
                    initializeSelect2ForField($(valueInput));
                }
            });

            // Initially disable the input
            valueInput.disabled = true;
        }

        // Initialize Select2 for fields with data URLs (but keep them disabled)
        if (hasDataUrl && $(valueInput).hasClass('select2-dropdown')) {
            // We will initialize Select2 when the field is enabled
            $(valueInput).attr('data-select2-initialized', 'false');
        }
    });

    // Show the modal
    $(`#${tableInstance.bulkUpdateModal.modalId}`).modal('show');

    // Initialize Select2 dropdowns if available
    if (typeof $.fn.select2 !== 'undefined') {
        setTimeout(() => {
            try {
                $('.select2-dropdown').each(function() {
                    const $select = $(this);
                    if (!$select.prop('disabled') && $select.attr('data-select2-initialized') !== 'true') {
                        initializeSelect2ForField($select);
                    }
                });
            } catch (e) {
                console.warn('Error initializing Select2:', e);
            }
        }, 300);
    }
}

/**
 * Initialize Select2 for a dropdown field if Select2 is available
 * @param {jQuery} $select - jQuery element for the select
 */
function initializeSelect2ForField($select) {
    if (typeof $.fn.select2 === 'undefined') return;

    const dataUrl = $select.data('url');
    if (!dataUrl) return;

    try {
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
                    let items = [];
                    if (response && response.data && response.data.data) {
                        items = response.data.data.map(item => ({
                            id: item.id,
                            text: item.text,
                            selected: item.selected || false
                        }));
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
    } catch (e) {
        console.warn('Error initializing Select2:', e);
    }
}

/**
 * Submit the bulk update form
 * @param {Object} tableInstance - Table instance configuration
 */
function submitBulkUpdate(tableInstance) {
    const form = document.getElementById(tableInstance.bulkUpdateModal.formId);

    if (!form) return;

    // Get selected record IDs
    const ids = tableInstance.$grid.jqGrid('getGridParam', 'selarrrow');
    if (!ids || ids.length === 0) {
        utils.notify('warning', 'No items selected', tableInstance);
        return;
    }

    // Build action object with field updates
    const action = {};

    // Get all field checkboxes
    const enabledCheckboxes = form.querySelectorAll('input[name$="-enabled"]:checked');

    // For each enabled field, get the value
    enabledCheckboxes.forEach(checkbox => {
        const fieldName = checkbox.name.replace('-enabled', '');
        const valueInput = form.querySelector(`[name="${fieldName}-value"]`);

        if (valueInput) {
            let value = valueInput.value;

            // Handle checkbox values
            if (valueInput.type === 'checkbox') {
                value = valueInput.checked;
            }

            // Add to action object
            action[fieldName] = value;
        }
    });

    // Check if any fields were selected
    if (Object.keys(action).length === 0) {
        utils.notify('warning', 'Please enable at least one field to update', tableInstance);
        return;
    }

    // Get scope (specific or all)
    const scope = $(`input[type='radio'][name='${tableInstance.id}_bulk_selection_choice']:checked`).val();

    // Confirm before proceeding
    let confirmMessage = '';
    if (scope === 'specific') {
        confirmMessage = `Are you sure you want to update these ${ids.length} items?`;
    } else if (scope === 'all') {
        confirmMessage = 'Are you sure you want to update all items?';
    }

    if (!confirm(confirmMessage)) {
        return;
    }
    
    // Allow user to apply hooks before submitting bulk update
    if (typeof window.jqGridConfig.hooks.beforeSubmitBulkUpdate === 'function') {
        const shouldContinue = window.jqGridConfig.hooks.beforeSubmitBulkUpdate(tableInstance, ids, action, scope);
        if (shouldContinue === false) {
            return; // Allow cancellation of update
        }
    }

    // Show loading state
    const submitButton = document.getElementById(tableInstance.bulkUpdateModal.submitButtonId);
    if (submitButton) {
        submitButton.disabled = true;
        submitButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Updating...';
    }

    // API URL for this table instance
    const apiUrl = getApiUrl(tableInstance, 'bulk_action');

    // Send request
    $.ajax({
        url: apiUrl,
        method: 'POST',
        data: JSON.stringify({
            ids: ids,
            filters: tableInstance.$grid.jqGrid('getGridParam', 'postData').filters,
            scope: scope,
            action: action
        }),
        contentType: 'application/json',
        // CSRF token is handled by $.ajaxSetup in jqgrid-csrf.js
        success: function(response) {
            // Hide modal
            $(`#${tableInstance.bulkUpdateModal.modalId}`).modal('hide');

            // Show success message
            utils.notify('success', response.message || 'Bulk update successful', tableInstance);

            // Reload grid
            tableInstance.$grid.trigger('reloadGrid');

            // Reset button
            if (submitButton) {
                submitButton.disabled = false;
                submitButton.innerHTML = 'Update Selected Items';
            }
            
            // Allow user to apply hooks after submitting bulk update
            if (typeof window.jqGridConfig.hooks.afterSubmitBulkUpdate === 'function') {
                window.jqGridConfig.hooks.afterSubmitBulkUpdate(tableInstance, ids, action, scope, response);
            }
        },
        error: function(xhr) {
            // Reset button
            if (submitButton) {
                submitButton.disabled = false;
                submitButton.innerHTML = 'Update Selected Items';
            }

            // Show error message
            let errorMessage = 'An error occurred during bulk update';

            if (xhr.responseJSON && xhr.responseJSON.message) {
                errorMessage = xhr.responseJSON.message;
            }

            utils.notify('error', errorMessage, tableInstance);
        },
        complete: function() {
            // Reset selection info
            updateInstanceSelection(tableInstance);
        }
    });
}

/**
 * Perform bulk delete on selected records
 * @param {Object} tableInstance - Table instance configuration
 */
function performBulkDelete(tableInstance) {
    const selectedIds = tableInstance.$grid.jqGrid('getGridParam', 'selarrrow');
    if (!selectedIds || selectedIds.length === 0) {
        utils.notify('warning', 'Please select at least one row', tableInstance);
        return;
    }

    // Get scope (specific or all)
    const scope = $(`input[type='radio'][name='${tableInstance.id}_bulk_selection_choice']:checked`).val();

    // Confirm before proceeding
    let confirmMessage = '';
    if (scope === 'specific') {
        confirmMessage = `Are you sure you want to delete these ${selectedIds.length} items?`;
    } else if (scope === 'all') {
        confirmMessage = 'Are you sure you want to delete all items?';
    }

    if (!confirm(confirmMessage)) {
        return;
    }

    // API URL for this table instance
    const apiUrl = getApiUrl(tableInstance, 'bulk_action');

    $.ajax({
        url: apiUrl,
        method: 'POST',
        data: JSON.stringify({
            ids: selectedIds,
            filters: tableInstance.$grid.jqGrid('getGridParam', 'postData').filters,
            scope: scope,
            action: {
                _delete: true
            }
        }),
        contentType: 'application/json',
        // CSRF token is handled by $.ajaxSetup in jqgrid-csrf.js
        success: function(response) {
            utils.notify('success', response.message || 'Items deleted successfully', tableInstance);

            // Reload grid
            tableInstance.$grid.trigger('reloadGrid');
        },
        error: function(xhr) {
            let errorMessage = 'An error occurred during bulk delete';

            if (xhr.responseJSON && xhr.responseJSON.message) {
                errorMessage = xhr.responseJSON.message;
            }

            utils.notify('error', errorMessage, tableInstance);
        }
    });
}

/**
 * Update selection information in the toolbar
 * @param {Object} tableInstance - Table instance configuration
 */
function updateInstanceSelection(tableInstance) {
    const selectedIds = tableInstance.$grid.jqGrid('getGridParam', 'selarrrow');
    const count = selectedIds ? selectedIds.length : 0;

    // Store selected IDs in table instance
    tableInstance.selectionIds = selectedIds || [];

    // Update count display
    const countElement = document.getElementById(tableInstance.toolbarSettings.selectedCountId);
    if (countElement) {
        countElement.textContent = count;
    }

    // Show/hide selection info and bulk action buttons
    const selectionInfo = document.getElementById(tableInstance.toolbarSettings.selectionInfoId);
    const bulkButtons = document.getElementById(tableInstance.toolbarSettings.bulkActionsContainerId);

    if (selectionInfo) {
        selectionInfo.style.display = count > 0 ? 'block' : 'none';
    }

    if (bulkButtons) {
        bulkButtons.style.display = count > 0 ? 'flex' : 'none';
    }
}

/**
 * Fetch additional data for a specific table instance
 * @param {Object} tableInstance - Table instance configuration
 */
function fetchAdditionalDataForTable(tableInstance) {
    const apiUrl = getApiUrl(tableInstance, 'additional_data_response');

    $.ajax({
        url: apiUrl,
        method: 'GET',
        success: function(response) {
            const data = response.data;
            if (data) {
                // Store header titles in table instance
                if (data.header_titles) {
                    tableInstance.headerTitles = data.header_titles;
                }

                // Update bulk action configuration if available
                if (data.bulk_action_config) {
                    initializeBulkActionsForTable(tableInstance, data.bulk_action_config);
                }

                // Apply conditional formatting or other enhancements
                if (data.conditional_formatting || data.highlight_rules) {
                    applyConditionalFormatting(tableInstance, data.conditional_formatting, data.highlight_rules);
                }


                // Trigger custom event when additional data is loaded
                if (typeof tableInstance.options.onAdditionalDataLoaded === 'function') {
                    tableInstance.options.onAdditionalDataLoaded(tableInstance, data);
                }
            }
        },
        error: function(xhr, status, error) {
            console.error(`Error loading additional data for ${tableInstance.tableName}:`, error);
        }
    });
}

/**
 * Apply conditional formatting to cells and rows for a specific table
 * @param {Object} tableInstance - Table instance configuration
 * @param {Object} conditionalFormatting - Column-based formatting rules
 * @param {Array} highlightRules - Row-based highlighting rules
 */
function applyConditionalFormatting(tableInstance, conditionalFormatting, highlightRules) {
    const $grid = tableInstance.$grid;

    // Cell-level formatting
    if (conditionalFormatting) {
        for (const fieldName in conditionalFormatting) {
            const rules = conditionalFormatting[fieldName];
            const rows = $grid.jqGrid('getDataIDs');

            rows.forEach(rowId => {
                const rowData = $grid.jqGrid('getRowData', rowId);
                const cellValue = rowData[fieldName];

                // Check each rule
                rules.forEach(rule => {
                    let match = false;

                    // Evaluate rule
                    if (rule.operator === 'eq' && cellValue == rule.value) {
                        match = true;
                    } else if (rule.operator === 'ne' && cellValue != rule.value) {
                        match = true;
                    } else if (rule.operator === 'gt' && parseFloat(cellValue) > parseFloat(rule.value)) {
                        match = true;
                    } else if (rule.operator === 'lt' && parseFloat(cellValue) < parseFloat(rule.value)) {
                        match = true;
                    } else if (rule.operator === 'contains' && String(cellValue).indexOf(rule.value) >= 0) {
                        match = true;
                    }

                    // Apply formatting if rule matched
                    if (match) {
                        $grid.jqGrid('setCell', rowId, fieldName, '', {
                            color: rule.textColor || '',
                            background: rule.backgroundColor || ''
                        });
                    }
                });
            });
        }
    }

    // Row-level highlighting
    if (highlightRules) {
        const rows = $grid.jqGrid('getDataIDs');

        rows.forEach(rowId => {
            const rowData = $grid.jqGrid('getRowData', rowId);

            // Check each highlight rule
            for (let j = 0; j < highlightRules.length; j++) {
                const rule = highlightRules[j];
                const fieldName = rule.field;
                const cellValue = rowData[fieldName];
                let match = false;

                // Evaluate rule
                if (rule.operator === 'eq' && cellValue == rule.value) {
                    match = true;
                } else if (rule.operator === 'ne' && cellValue != rule.value) {
                    match = true;
                } else if (rule.operator === 'gt' && parseFloat(cellValue) > parseFloat(rule.value)) {
                    match = true;
                } else if (rule.operator === 'lt' && parseFloat(cellValue) < parseFloat(rule.value)) {
                    match = true;
                } else if (rule.operator === 'contains' && String(cellValue).indexOf(rule.value) >= 0) {
                    match = true;
                }

                // Apply row highlighting if rule matched
                if (match) {
                    $(`#${rowId}`).addClass(rule.cssClass);
                    break; // Stop checking rules after first match
                }
            }
        });
    }
}

/**
 * Show message in grid message area
 * @param {Object} tableInstance - Table instance configuration
 * @param {string} type - Message type (success, info, warning, error)
 * @param {string} message - Message text
 */
function showMessage(tableInstance, type, message) {
    // First, try to use the notification system
    if (utils.notify(type, message, tableInstance)) {
        return;
    }
    
    // Fallback to message container if notification system returns false
    const alertClass = type === 'success' ? 'alert-success' : 
                      type === 'warning' ? 'alert-warning' : 
                      type === 'error' ? 'alert-danger' : 'alert-info';
    
    // Find message container for this table
    const messageContainerId = tableInstance.toolbarSettings.messageContainerId;
    const $messageContainer = $(`#${messageContainerId}`);
    
    if ($messageContainer.length) {
        $messageContainer
            .removeClass('alert-success alert-info alert-warning alert-danger')
            .addClass(alertClass)
            .html(message)
            .show();
        
        setTimeout(() => $messageContainer.fadeOut(), 5000);
    } else {
        // Fallback to global message container
        $('#gridMessages')
            .removeClass('alert-success alert-info alert-warning alert-danger')
            .addClass(alertClass)
            .html(message)
            .show();
        
        setTimeout(() => $('#gridMessages').fadeOut(), 5000);
    }
}

/**
 * Get filter query string for a specific table
 * @param {Object} tableInstance - Table instance configuration
 * @returns {string} Query string with filter parameters
 */
function getFilterQueryString(tableInstance) {
    const postData = tableInstance.$grid.jqGrid('getGridParam', 'postData');
    if (!postData) return '';

    const params = new URLSearchParams();
    for (const key in postData) {
        if (postData.hasOwnProperty(key)) {
            params.append(key, postData[key]);
        }
    }

    return params.toString();
}

/**
 * Refresh and reload a specific table
 * @param {Object} tableInstance - Table instance configuration
 */
function refreshTable(tableInstance) {
    if (tableInstance.$grid) {
        tableInstance.$grid.trigger('reloadGrid');
    }
}


// Make functions available in global namespace
window.tables = window.tables || {};
window.jqGridManager = {
    // Public API
    initializeTableInstance: initializeTableInstance,
    refreshTable: refreshTable,
    getFilterQueryString: getFilterQueryString,
    showMessage: showMessage,
    utils: utils,
    
    // Initialize all tables with jqGrid class
    initializeAll: function() {
        // Look for all jqGrid tables on the page
        $('.jqGrid').each(function() {
            const $grid = $(this);
            const tableId = $grid.attr('id') || `jqGrid_${Math.random().toString(36).substring(2, 9)}`;

            // If grid doesn't have an ID, assign one
            if (!$grid.attr('id')) {
                $grid.attr('id', tableId);
            }

            // Get app name and table name
            let appName = '';
            let tableName = '';

            // Try to get from data attributes
            if ($grid.data('app-name') && $grid.data('table-name')) {
                appName = $grid.data('app-name');
                tableName = $grid.data('table-name');
            }
            // Try to extract from URL
            else if ($grid.data('url')) {
                const url = $grid.data('url');
                const matches = url.match(/\/api\/([^\/]+)\/([^\/]+)\//);
                if (matches && matches.length === 3) {
                    appName = matches[1];
                    tableName = matches[2];
                }
            }
            // Fallback to global variables
            else if (window.app_name && window.table_name) {
                appName = window.app_name;
                tableName = window.table_name;
            }

            // Initialize table instance if we have app name and table name
            if (appName && tableName) {
                window.initializeTableInstance(tableId, appName, tableName, {
                    pagerSelector: `#${tableId}Pager`
                });
            }
        });
    }
};

// Initialize all tables when document is ready
$(document).ready(function() {
    window.jqGridManager.initializeAll();
});