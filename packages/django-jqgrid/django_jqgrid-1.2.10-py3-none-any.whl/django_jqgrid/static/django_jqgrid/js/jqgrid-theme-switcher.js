/**
 * jqGrid Theme Switcher
 * Allows dynamic theme switching for jqGrid instances
 */

(function($) {
    'use strict';
    
    window.jqGridThemeSwitcher = {
        // Available themes configuration
        themes: {
            'bootstrap': {
                name: 'Bootstrap 3',
                styleUI: 'Bootstrap',
                cssFile: 'ui.jqgrid-bootstrap.css',
                bootstrapVersion: '3.4.1'
            },
            'bootstrap4': {
                name: 'Bootstrap 4',
                styleUI: 'Bootstrap4',
                cssFile: 'ui.jqgrid-bootstrap4.css',
                bootstrapVersion: '4.6.0'
            },
            'bootstrap5': {
                name: 'Bootstrap 5',
                styleUI: 'Bootstrap5',
                cssFile: 'ui.jqgrid-bootstrap5.css',
                bootstrapVersion: '5.1.3'
            },
            'jqueryui': {
                name: 'jQuery UI',
                styleUI: 'jQueryUI',
                cssFile: 'ui.jqgrid.css',
                bootstrapVersion: null
            }
        },
        
        // Icon sets configuration
        iconSets: {
            'fontAwesome': {
                name: 'Font Awesome',
                cssUrl: 'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css'
            },
            'jQueryUI': {
                name: 'jQuery UI Icons',
                cssUrl: null
            },
            'bootstrap': {
                name: 'Bootstrap Icons',
                cssUrl: 'https://cdn.jsdelivr.net/npm/bootstrap-icons@1.7.2/font/bootstrap-icons.css'
            },
            'glyph': {
                name: 'Glyphicons',
                cssUrl: null // Included with Bootstrap 3
            }
        },
        
        // Current theme
        currentTheme: window.jqGridThemeConfig ? window.jqGridThemeConfig.theme : 'bootstrap4',
        currentIconSet: window.jqGridThemeConfig ? window.jqGridThemeConfig.iconSet : 'fontAwesome',
        
        /**
         * Initialize theme switcher
         */
        init: function(options) {
            const defaults = {
                container: '#theme-switcher',
                showPreview: true,
                onChange: null
            };
            
            this.options = $.extend({}, defaults, options);
            
            if ($(this.options.container).length) {
                this.render();
            }
        },
        
        /**
         * Render theme switcher UI
         */
        render: function() {
            const html = `
                <div class="jqgrid-theme-switcher card">
                    <div class="card-header">
                        <h5 class="card-title mb-0">Grid Theme Settings</h5>
                    </div>
                    <div class="card-body">
                        <div class="form-group">
                            <label for="jqgrid-theme-select">Theme:</label>
                            <select id="jqgrid-theme-select" class="form-control">
                                ${Object.entries(this.themes).map(([key, theme]) => 
                                    `<option value="${key}" ${key === this.currentTheme ? 'selected' : ''}>${theme.name}</option>`
                                ).join('')}
                            </select>
                        </div>
                        
                        <div class="form-group">
                            <label for="jqgrid-iconset-select">Icon Set:</label>
                            <select id="jqgrid-iconset-select" class="form-control">
                                ${Object.entries(this.iconSets).map(([key, iconSet]) => 
                                    `<option value="${key}" ${key === this.currentIconSet ? 'selected' : ''}>${iconSet.name}</option>`
                                ).join('')}
                            </select>
                        </div>
                        
                        <button id="jqgrid-apply-theme" class="btn btn-primary">Apply Theme</button>
                        <button id="jqgrid-reset-theme" class="btn btn-secondary">Reset</button>
                        
                        ${this.options.showPreview ? '<div id="jqgrid-theme-preview" class="mt-3"></div>' : ''}
                    </div>
                </div>
            `;
            
            $(this.options.container).html(html);
            this.bindEvents();
        },
        
        /**
         * Bind events
         */
        bindEvents: function() {
            const self = this;
            
            $('#jqgrid-apply-theme').on('click', function() {
                const theme = $('#jqgrid-theme-select').val();
                const iconSet = $('#jqgrid-iconset-select').val();
                self.switchTheme(theme, iconSet);
            });
            
            $('#jqgrid-reset-theme').on('click', function() {
                self.resetTheme();
            });
            
            // Preview on change
            if (this.options.showPreview) {
                $('#jqgrid-theme-select, #jqgrid-iconset-select').on('change', function() {
                    self.updatePreview();
                });
            }
        },
        
        /**
         * Switch theme
         */
        switchTheme: function(theme, iconSet) {
            // Remove old theme CSS
            $('link[href*="ui.jqgrid"]').remove();
            
            // Add new theme CSS
            const themeConfig = this.themes[theme];
            if (themeConfig) {
                $('head').append(
                    `<link rel="stylesheet" href="/static/django_jqgrid/plugins/jqGrid/css/${themeConfig.cssFile}">`
                );
                
                // Update Bootstrap if needed
                if (themeConfig.bootstrapVersion) {
                    this.updateBootstrap(themeConfig.bootstrapVersion);
                }
            }
            
            // Update icon set
            this.updateIconSet(iconSet);
            
            // Update all grids
            this.updateAllGrids(theme, iconSet);
            
            // Save preference
            this.savePreference(theme, iconSet);
            
            // Trigger callback
            if (typeof this.options.onChange === 'function') {
                this.options.onChange(theme, iconSet);
            }
            
            this.currentTheme = theme;
            this.currentIconSet = iconSet;
        },
        
        /**
         * Update Bootstrap version
         */
        updateBootstrap: function(version) {
            // Remove old Bootstrap
            $('link[href*="bootstrap.min.css"]').remove();
            
            // Add new Bootstrap
            $('head').prepend(
                `<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@${version}/dist/css/bootstrap.min.css">`
            );
        },
        
        /**
         * Update icon set
         */
        updateIconSet: function(iconSet) {
            const iconConfig = this.iconSets[iconSet];
            
            // Remove old icon CSS
            $('link[href*="font-awesome"], link[href*="bootstrap-icons"]').remove();
            
            // Add new icon CSS if needed
            if (iconConfig && iconConfig.cssUrl) {
                $('head').append(`<link rel="stylesheet" href="${iconConfig.cssUrl}">`);
            }
        },
        
        /**
         * Update all grid instances
         */
        updateAllGrids: function(theme, iconSet) {
            const themeConfig = this.themes[theme];
            
            // Update each grid instance
            Object.keys(window.tables || {}).forEach(tableId => {
                const tableInstance = window.tables[tableId];
                if (tableInstance && tableInstance.$grid) {
                    // Update grid options
                    tableInstance.$grid.jqGrid('setGridParam', {
                        styleUI: themeConfig.styleUI,
                        iconSet: iconSet
                    });
                    
                    // Refresh grid UI
                    this.refreshGridUI(tableInstance);
                }
            });
            
            // Update global config
            window.jqGridThemeConfig = {
                theme: theme,
                styleUI: themeConfig.styleUI,
                iconSet: iconSet
            };
        },
        
        /**
         * Refresh grid UI elements
         */
        refreshGridUI: function(tableInstance) {
            // Get current grid state
            const gridParam = tableInstance.$grid.jqGrid('getGridParam');
            const colModel = gridParam.colModel;
            
            // Destroy and recreate pager buttons
            const pagerId = gridParam.pager;
            if (pagerId) {
                // Store current page
                const currentPage = gridParam.page;
                
                // Refresh navigation buttons
                tableInstance.$grid.jqGrid('navGrid', pagerId, {refresh: true});
                
                // Restore page
                tableInstance.$grid.jqGrid('setGridParam', {page: currentPage}).trigger('reloadGrid');
            }
        },
        
        /**
         * Reset to default theme
         */
        resetTheme: function() {
            const defaultTheme = window.jqGridThemeConfig ? window.jqGridThemeConfig.theme : 'bootstrap4';
            const defaultIconSet = window.jqGridThemeConfig ? window.jqGridThemeConfig.iconSet : 'fontAwesome';
            
            $('#jqgrid-theme-select').val(defaultTheme);
            $('#jqgrid-iconset-select').val(defaultIconSet);
            
            this.switchTheme(defaultTheme, defaultIconSet);
        },
        
        /**
         * Update preview
         */
        updatePreview: function() {
            const theme = $('#jqgrid-theme-select').val();
            const iconSet = $('#jqgrid-iconset-select').val();
            const themeConfig = this.themes[theme];
            
            const preview = `
                <div class="alert alert-info">
                    <h6>Preview:</h6>
                    <p>Theme: <strong>${themeConfig.name}</strong></p>
                    <p>Style UI: <code>${themeConfig.styleUI}</code></p>
                    <p>Icon Set: <strong>${this.iconSets[iconSet].name}</strong></p>
                    ${themeConfig.bootstrapVersion ? 
                        `<p>Bootstrap Version: <code>${themeConfig.bootstrapVersion}</code></p>` : ''}
                </div>
            `;
            
            $('#jqgrid-theme-preview').html(preview);
        },
        
        /**
         * Save theme preference
         */
        savePreference: function(theme, iconSet) {
            if (typeof Storage !== 'undefined') {
                localStorage.setItem('jqgrid_theme', theme);
                localStorage.setItem('jqgrid_iconset', iconSet);
            }
            
            // Save to server if endpoint is available
            if (window.jqGridConfig && window.jqGridConfig.savePreferencesUrl) {
                $.ajax({
                    url: window.jqGridConfig.savePreferencesUrl,
                    method: 'POST',
                    data: JSON.stringify({
                        theme: theme,
                        iconSet: iconSet
                    }),
                    contentType: 'application/json',
                    // CSRF token is handled by $.ajaxSetup in jqgrid-csrf.js
                });
            }
        },
        
        /**
         * Load saved preference
         */
        loadPreference: function() {
            if (typeof Storage !== 'undefined') {
                const savedTheme = localStorage.getItem('jqgrid_theme');
                const savedIconSet = localStorage.getItem('jqgrid_iconset');
                
                if (savedTheme && this.themes[savedTheme]) {
                    this.currentTheme = savedTheme;
                }
                
                if (savedIconSet && this.iconSets[savedIconSet]) {
                    this.currentIconSet = savedIconSet;
                }
                
                return {
                    theme: this.currentTheme,
                    iconSet: this.currentIconSet
                };
            }
            
            return null;
        }
    };
    
    // Auto-initialize if container exists
    $(document).ready(function() {
        // Load saved preference
        const saved = window.jqGridThemeSwitcher.loadPreference();
        if (saved && saved.theme !== window.jqGridThemeSwitcher.currentTheme) {
            window.jqGridThemeSwitcher.switchTheme(saved.theme, saved.iconSet);
        }
        
        // Initialize switcher UI if container exists
        if ($('#theme-switcher').length) {
            window.jqGridThemeSwitcher.init();
        }
    });
    
})(jQuery);