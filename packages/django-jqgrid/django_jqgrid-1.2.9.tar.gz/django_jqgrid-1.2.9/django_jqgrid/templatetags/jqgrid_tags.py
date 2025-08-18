import json

from django import template
from django.utils.safestring import mark_safe
from django.conf import settings

register = template.Library()


@register.simple_tag
def jqgrid_css(theme='bootstrap4'):
    """
    Includes the required CSS files for jqGrid.
    
    Args:
        theme: Theme name - 'bootstrap', 'bootstrap4', 'bootstrap5', 'jqueryui', or 'custom'
               Default is 'bootstrap4'
    """
    # Base CSS files always needed
    css = [
        # jQuery UI CSS (required for dialogs and date pickers)
        '<link rel="stylesheet" href="https://code.jquery.com/ui/1.13.2/themes/ui-lightness/jquery-ui.css">',
    ]
    
    # Add theme-specific CSS
    theme_map = {
        'bootstrap': 'ui.jqgrid-bootstrap.css',
        'bootstrap4': 'ui.jqgrid-bootstrap4.css',
        'bootstrap5': 'ui.jqgrid-bootstrap5.css',
        'jqueryui': 'ui.jqgrid.css',
        'custom': getattr(settings, 'JQGRID_CUSTOM_THEME_CSS', 'ui.jqgrid-bootstrap4.css')
    }
    
    # Get theme file or default to bootstrap4
    theme_file = theme_map.get(theme, 'ui.jqgrid-bootstrap4.css')
    css.append(f'<link rel="stylesheet" href="/static/django_jqgrid/plugins/jqGrid/css/{theme_file}">')
    
    # Add addons CSS
    css.append('<link rel="stylesheet" href="/static/django_jqgrid/plugins/jqGrid/css/addons/ui.multiselect.css">')
    
    # Add custom override styles
    css.append('<link rel="stylesheet" href="/static/django_jqgrid/css/jqgrid-bootstrap.css">')
    
    return mark_safe('\n'.join(css))


@register.simple_tag
def jqgrid_theme(theme=None, icon_set=None, custom_css=None):
    """
    Configure jqGrid theme with CSS and JavaScript settings.
    
    Args:
        theme: Theme name - 'bootstrap', 'bootstrap4', 'bootstrap5', 'jqueryui'
               If None, uses JQGRID_THEME from settings (default: 'bootstrap4')
        icon_set: Icon set - 'fontAwesome', 'jQueryUI', 'bootstrap', 'glyph'
                  If None, uses JQGRID_ICON_SET from settings (default: 'fontAwesome')
        custom_css: Path to custom CSS file (optional)
                    Can also be set via JQGRID_CUSTOM_CSS in settings
    
    Example:
        {% jqgrid_theme %}  # Uses settings
        {% jqgrid_theme 'bootstrap5' 'fontAwesome' %}
        {% jqgrid_theme theme='bootstrap4' custom_css='/static/css/my-grid-theme.css' %}
    
    Settings example:
        JQGRID_THEME = 'bootstrap5'
        JQGRID_ICON_SET = 'fontAwesome'
        JQGRID_CUSTOM_CSS = '/static/css/custom-grid.css'
    """
    # Get theme from parameter or settings
    if theme is None:
        theme = getattr(settings, 'JQGRID_THEME', 'bootstrap4')
    
    # Get icon set from parameter or settings
    if icon_set is None:
        icon_set = getattr(settings, 'JQGRID_ICON_SET', 'fontAwesome')
    
    # Get custom CSS from parameter or settings
    if custom_css is None:
        custom_css = getattr(settings, 'JQGRID_CUSTOM_CSS', None)
    
    # CSS includes
    css_html = jqgrid_css(theme)
    
    # Add Font Awesome if using fontAwesome icons
    if icon_set == 'fontAwesome':
        css_html = '<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css">\n' + css_html
    
    # Add Bootstrap CSS if not already included and using Bootstrap theme
    if 'bootstrap' in theme:
        bootstrap_version = '4.6.0' if theme == 'bootstrap4' else '5.1.3' if theme == 'bootstrap5' else '3.4.1'
        css_html = f'<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@{bootstrap_version}/dist/css/bootstrap.min.css">\n' + css_html
    
    # Add custom CSS if provided
    if custom_css:
        css_html += f'\n<link rel="stylesheet" href="{custom_css}">'
    
    # JavaScript configuration for theme
    style_ui = 'Bootstrap' if theme == 'bootstrap' else 'Bootstrap4' if theme == 'bootstrap4' else 'Bootstrap5' if theme == 'bootstrap5' else 'jQueryUI'
    
    js_config = f"""
<script>
// Configure jqGrid theme settings
window.jqGridThemeConfig = {{
    styleUI: '{style_ui}',
    iconSet: '{icon_set}',
    theme: '{theme}'
}};

// Apply theme to default grid options
window.jqGridConfig = window.jqGridConfig || {{}};
window.jqGridConfig.defaultGridOptions = window.jqGridConfig.defaultGridOptions || {{}};
Object.assign(window.jqGridConfig.defaultGridOptions, {{
    styleUI: window.jqGridThemeConfig.styleUI,
    iconSet: window.jqGridThemeConfig.iconSet
}});

// Apply responsive classes based on theme
if (window.jqGridThemeConfig.theme.includes('bootstrap')) {{
    window.jqGridConfig.defaultGridOptions.responsiveClass = 'table-responsive';
}}
</script>
"""
    
    return mark_safe(css_html + '\n' + js_config)


@register.simple_tag
def jqgrid_dependencies():
    """
    Includes the required dependency JavaScript files for jqGrid.
    Call this before jqgrid_js() if jQuery and jQuery UI are not already loaded.
    """
    js = [
        # jQuery Core
        '<script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>',

        # jQuery UI and dependencies
        '<script src="https://code.jquery.com/ui/1.13.2/jquery-ui.min.js"></script>',

        # XLSX support for import/export
        '<script src="https://cdnjs.cloudflare.com/ajax/libs/xlsx/0.18.5/xlsx.full.min.js"></script>',
    ]
    return mark_safe('\n'.join(js))


@register.simple_tag
def jqgrid_js():
    """
    Includes the required JavaScript files for jqGrid.
    """
    from django.templatetags.static import static
    
    js_files = [
        # CSRF token setup (should be loaded first)
        'django_jqgrid/js/jqgrid-csrf.js',
        
        # jqGrid core files
        'django_jqgrid/plugins/jqGrid/js/i18n/grid.locale-en.js',
        'django_jqgrid/plugins/jqGrid/js/jquery.jqGrid.min.js',

        # Additional plugins
        'django_jqgrid/plugins/jqGrid/plugins/jquery.contextmenu.js',
        'django_jqgrid/plugins/jqGrid/plugins/grid.postext.js',
        'django_jqgrid/plugins/jqGrid/plugins/jquery.tablednd.js',

        # Our custom jqGrid modules
        'django_jqgrid/js/jqgrid-config.js',
        'django_jqgrid/js/jqgrid-core.js',
        # Note: jqgrid-integration.js should be loaded after jqgrid-core.js
    ]
    
    js = [f'<script src="{static(file)}"></script>' for file in js_files]
    return mark_safe('\n'.join(js))


@register.inclusion_tag('django_jqgrid/grid_tag.html')
def jqgrid(grid_id, app_name, model_name, grid_title=None,
           custom_formatters=None, custom_buttons=None, custom_bulk_actions=None,
           on_grid_complete=None, on_select_row=None, on_select_all=None,
           on_init_complete=None, extra_options=None, include_import_export=True):
    """
    Renders a jqGrid with the specified options.
    
    Args:
        grid_id (str): ID for the grid element in HTML
        app_name (str): Django app name containing the model
        model_name (str): Django model name (lowercase)
        grid_title (str, optional): Title to display above the grid
        custom_formatters (dict, optional): Dictionary of custom formatter functions
        custom_buttons (dict, optional): Dictionary of custom button configurations
        custom_bulk_actions (dict, optional): Dictionary of custom bulk action configurations
        on_grid_complete (str, optional): JavaScript function to call when grid completes loading
        on_select_row (str, optional): JavaScript function to call when a row is selected
        on_select_all (str, optional): JavaScript function to call when all rows are selected
        on_init_complete (str, optional): JavaScript function to call when grid initialization completes
        extra_options (str, optional): Additional options to pass to initializeTableInstance
        include_import_export (bool, optional): Whether to include import/export buttons (default: True)
        
    Returns:
        dict: Context for the template rendering
        
    Examples:
        {% jqgrid "users_grid" "mainapp" "user" "Users" %}
        
        {% jqgrid "users_grid" "mainapp" "user" "Users" include_import_export=False %}
    """
    # Convert dictionary objects to JSON strings if provided
    if custom_formatters:
        if isinstance(custom_formatters, dict):
            custom_formatters = json.dumps(custom_formatters)

    if custom_buttons:
        if isinstance(custom_buttons, dict):
            custom_buttons = json.dumps(custom_buttons)

    if custom_bulk_actions:
        if isinstance(custom_bulk_actions, dict):
            custom_bulk_actions = json.dumps(custom_bulk_actions)

    return {
        'grid_id': grid_id,
        'app_name': app_name,
        'model_name': model_name,
        'grid_title': grid_title,
        'custom_formatters': custom_formatters,
        'custom_buttons': custom_buttons,
        'custom_bulk_actions': custom_bulk_actions,
        'on_grid_complete': on_grid_complete,
        'on_select_row': on_select_row,
        'on_select_all': on_select_all,
        'on_init_complete': on_init_complete,
        'extra_options': extra_options,
        'include_import_export': include_import_export
    }


@register.filter(is_safe=True)
def js_function(value):
    """
    Filter to safely render a JavaScript function string in a template.
    This helps avoid issues with escaping quotes and newlines.
    
    Usage:
        {{ my_js_function|js_function }}
    """
    if not value:
        return ''

    # Make sure the value is properly JSON serialized
    # but only if it's not already a string that looks like a function
    if not isinstance(value, str) or not value.strip().startswith('function'):
        value = json.dumps(value)

    return mark_safe(value)
