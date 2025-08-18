from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.cache import cache
from rest_framework.decorators import action
from django_jqgrid.utils import get_content_type_cached


def get_setting(key, default=None):
    """Safely get a setting or return default if not found"""
    return getattr(settings, key, default)


class JqGridConfigMixin:
    """
    Enhanced jqGrid configuration mixin that dynamically builds grid config
    while maintaining output compatibility with legacy format and supporting settings-based configuration
    """
    key_field = "id"
    additional_data = {}

    # Get configuration from settings or use defaults
    JQGRID_DEFAULT_FIELD_CONFIG = {
        "UpperCharField": {'stype': 'text', 'search_ops': ["eq", "ne", "cn", "nc", "bw", "bn", "ew", "en"], 'sortable': True},
        "EmailField": {'stype': 'email', 'formatter': 'email',
                       'search_ops': ["eq", "ne", "cn", "nc", "bw", "bn", "ew", "en"], 'sortable': True},
        "ImageField": {'stype': 'text', 'formatter': 'image',
                       'search_ops': ["eq", "ne", "cn", "nc", "bw", "bn", "ew", "en"], 'sortable': False},
        "FileField": {'stype': 'text', 'formatter': 'file',
                      'search_ops': ["eq", "ne", "cn", "nc", "bw", "bn", "ew", "en"], 'sortable': False},
        "URLField": {'stype': 'text', 'formatter': 'link',
                     'search_ops': ["eq", "ne", "cn", "nc", "bw", "bn", "ew", "en"], 'sortable': True},
        "PhoneNumberField": {'stype': 'text', 'formatter': 'mobile',
                             'search_ops': ["eq", "ne", "cn", "nc", "bw", "bn", "ew", "en"], 'sortable': True},
        'CharField': {'stype': 'text', 'search_ops': ["eq", "ne", "cn", "nc", "bw", "bn", "ew", "en"], 'sortable': True},
        'TextField': {'stype': 'text', 'search_ops': ["eq", "ne", "cn", "nc", "bw", "bn", "ew", "en"], 'sortable': True},
        'JSONField': {'stype': 'textarea', 'formatter': 'json',
                      'search_ops': ["eq", "ne", "cn", "nc", "bw", "bn", "ew", "en"], 'sortable': False},
        'IntegerField': {'stype': 'integer', 'align': 'right', 'formatter': 'integer',
                         'search_ops': ["eq", "ne", "lt", "le", "gt", "ge"], 'sortable': True},
        'PositiveIntegerField': {'stype': 'integer', 'align': 'right', 'formatter': 'integer',
                                 'search_ops': ["eq", "ne", "lt", "le", "gt", "ge"], 'sortable': True},
        'FloatField': {'stype': 'number', 'align': 'right', 'formatter': 'number',
                       'search_ops': ["eq", "ne", "lt", "le", "gt", "ge"], 'sortable': True},
        'DecimalField': {'stype': 'number', 'align': 'right', 'formatter': 'number',
                         'search_ops': ["eq", "ne", "lt", "le", "gt", "ge"], 'needs_decimal_places': True, 'sortable': True},
        'BooleanField': {'stype': 'checkbox', 'align': 'center', 'formatter': 'checkbox', 'edittype': 'checkbox',
                         'editoptions': {"value": "1:0"}, 'search_ops': ["eq", "ne"], 'sortable': False},
        'DateField': {
            'stype': 'date', 'align': 'center', 'formatter': 'date',
            'formatoptions': {"srcformat": "ISO8601Short", "newformat": "Y-m-d"},
            'editoptions': {"dataInit": "initDatepicker", "datepicker": {"dateFormat": "yy-mm-dd"}},
            'search_ops': ["eq", "ne", "lt", "le", "gt", "ge"],
            'search_init': {"dataInit": "initDatepicker", "datepicker": {"dateFormat": "yy-mm-dd"}},
            'sortable': True
        },
        'DateTimeField': {
            'stype': 'datetime-local', 'align': 'center', 'formatter': 'datetimeLocal', 'edittype': 'datetime-local',
            'formatoptions': {"srcformat": "ISO8601", "newformat": "Y-m-d H:i:s"},
            'editoptions': {"dataInit": "initDatetimepicker",
                            "datetimepicker": {"dateFormat": "yy-mm-dd", "timeFormat": "HH:mm:ss"}},
            'search_ops': ["eq", "ne", "lt", "le", "gt", "ge"],
            'search_init': {"dataInit": "initDatetimepicker",
                            "datetimepicker": {"dateFormat": "yy-mm-dd", "timeFormat": "HH:mm:ss"}},
            'sortable': True
        },
        'ForeignKey': {'stype': 'text', 'formatter': 'select', 'search_ops': ["eq", "ne"], 'sortable': True}
    }
    FIELD_TYPE_CONFIGS = JQGRID_DEFAULT_FIELD_CONFIG  # Replace with get_setting() if needed

    # Default grid options
    JQGRID_DEFAULT_GRID_OPTIONS = {
        "datatype": "json",
        "mtype": "GET",
        "headertitles": True,
        "styleUI": "Bootstrap4",
        "iconSet": "fontAwesome",
        "responsive": True,
        "rowNum": 25,
        "rowList": [25, 50, 100, 500, 1000],
        "viewrecords": True,
        "gridview": True,
        "height": 400,
        "autowidth": True,
        "multiselect": True,
        "rownumbers": True,
        "altRows": True,
        "hoverrows": True,
        "sortable": True,
        "toolbar": [True, "both"],
        "forceFit": False,
        "autoresizeOnLoad": True,
        "footerrow": True,
        "userDataOnFooter": True,
        "toppager": True,
        "autoencode": True,
        "prmNames": {
            "page": "page",
            "rows": "rows",
            "sort": "sidx",
            "order": "sord",
            "search": "_search",
            "nd": "nd",
            "id": "id"
        },
        "jsonReader": {
            "root": "data.data",
            "page": "data.page",
            "total": "data.total_pages",
            "records": "data.records",
            "id": "id",
            "repeatitems": False
        }
    }
    DEFAULT_GRID_OPTIONS = JQGRID_DEFAULT_GRID_OPTIONS  # Replace with get_setting() if needed

    # Default method options
    JQGRID_DEFAULT_METHOD_OPTIONS = {
        "navGrid": {
            "selector": "#jqGridPager",
            "options": {
                "edit": True,
                "add": True,
                "del": True,
                "search": True,
                "refresh": True,
                "view": True,
                "position": "left",
                "closeOnEscape": True,
                "cloneToTop": True
            },
            "editOptions": {
                "closeOnEscape": True,
                "editCaption": "Edit Record",
                "recreateForm": True,
                "closeAfterEdit": True,
                "modal": True,
                "afterSubmit": "handleFormResponse",
                "errorTextFormat": "handleSubmitError",
                "reloadAfterSubmit": True
            },
            "addOptions": {
                "closeOnEscape": True,
                "recreateForm": True,
                "closeAfterAdd": True,
                "modal": True,
                "afterSubmit": "handleFormResponse",
                "errorTextFormat": "handleSubmitError",
                "reloadAfterSubmit": True,
                "mtype": "POST"
            },
            "delOptions": {
                "reloadAfterSubmit": True,
                "closeOnEscape": True,
                "modal": True
            },
            "searchOptions": {
                "closeOnEscape": True,
                "multipleSearch": True,
                "multipleGroup": True,
                "showQuery": True,
                "closeAfterSearch": True,
                "recreateFilter": True,
                "tmplNames": [],
                "tmplFilters": [],
                "tmplIds": []
            },
            "viewOptions": {
                "closeOnEscape": True,
                "width": 800,
                "modal": True,
                "top": 100,
                "left": 300
            }
        },
        "filterToolbar": {
            "options": {
                "stringResult": True,
                "defaultSearch": "cn",
                "searchOperators": True,
                "autosearch": True,
                "searchOnEnter": False
            }
        },
        "inlineNav": {
            "selector": "#jqGridPager",
            "options": {
                "edit": True,
                "add": True,
                "del": True,
                "cancel": True,
                "save": True
            }
        },
        "sortableRows": {
            "options": {
                "update": "handleRowOrderChange"
            }
        },
        "navButtonAdd": [
            {
                "selector": "#jqGridPager",
                "button": {
                    "caption": "Export",
                    "title": "Export Data",
                    "buttonicon": "fa fa-download",
                    "onClickButton": "handleExport"
                }
            },
            {
                "selector": "#jqGridPager",
                "button": {
                    "caption": "Import",
                    "title": "Import Data",
                    "buttonicon": "fa fa-upload",
                    "onClickButton": "handleImport"
                }
            }
        ]
    }
    DEFAULT_METHOD_OPTIONS = JQGRID_DEFAULT_METHOD_OPTIONS  # Replace with get_setting() if needed

    # Override field configuration in viewset
    jqgrid_field_overrides = {}

    def initgrid(self):
        """Initialize the grid configuration"""
        # Validate requirements
        if not hasattr(self, 'serializer_class'):
            raise ValueError("JqGridConfigMixin requires 'serializer_class' to be defined")

        # Set default key field if not defined
        if not hasattr(self, 'key_field'):
            self.key_field = 'id'

        # Initialize base components
        self.colmodel = [{
            "label": "Actions",
            "name": "actions",
            "formatter": "actions",
            "search": False,
            "sortable": False,
            "align": "center",
            "frozen": True,
            "width": 100
        }]
        self.colnames = ['Actions']

        # Get metadata from model and serializer
        self._get_model_metadata()

        # Initialize columns based on metadata
        self.initialize_columns()

        # Configure grid options
        self.configure_grid_options()
        self.configure_method_options()

        # Configure advanced features
        self._configure_frozen_columns()
        self._configure_grouping()
        self._configure_conditional_formatting()
        self._configure_highlight_rules()
        self._configure_bulk_actions()

        # Update grid options with feature flags
        self.jqgrid_options.update({
            'has_batch_actions': True,
            'has_frozen_columns': self.frozen_columns_enabled,
            'has_grouping': bool(self.groupable_fields),
            'has_conditional_formatting': bool(self.conditional_formatting),
            'has_highlight_rules': bool(getattr(self, 'highlight_rules', {}))
        })

        # Add import/export configurations if available
        if hasattr(self, 'import_config'):
            self.additional_data['import_config'] = self.import_config
        if hasattr(self, 'export_config'):
            self.additional_data['export_config'] = self.export_config

        # Add key_field to additional_data
        self.additional_data.update({'key_field': self.key_field})

        # Add bulk_action_config to additional_data
        if hasattr(self, 'bulk_action_config'):
            self.additional_data.update({'bulk_action_config': self.bulk_action_config})

    def _get_model_metadata(self):
        """Extract metadata from model and serializer"""
        # Get serializer fields
        serializer_class = self.serializer_class or self.get_serializer_class()
        if not serializer_class:
            raise TypeError(f"'{self.__class__.__name__}' must have a `serializer_class` attribute.")
        serializer = serializer_class()

        # Get field lists from viewset or use defaults
        self.visible_columns = getattr(self, 'visible_columns', list(serializer.get_fields().keys()))
        self.search_fields = getattr(self, 'search_fields', list(serializer.get_fields().keys()))
        self.ordering_fields = getattr(self, 'ordering_fields', list(serializer.get_fields().keys()))
        self.groupable_fields = getattr(self, 'groupable_fields', [])
        self.aggregation_fields = getattr(self, 'aggregation_fields', {})
        self.frozen_columns = getattr(self, 'frozen_columns', [])
        self.linked_fields = getattr(self, 'linked_fields', {})
        self.conditional_formatting = getattr(self, 'conditional_formatting', {})
        self.highlight_rules = getattr(self, 'highlight_rules', {})

        # Get model instance for metadata
        model = getattr(serializer_class.Meta, "model", None)

        # Extract field titles from model verbose_names
        self.header_titles = getattr(self, 'header_titles', {})
        if not self.header_titles and model:
            self.header_titles = {
                field.name: field.verbose_name.title()
                for field in model._meta.get_fields()
                if hasattr(field, 'verbose_name')
            }

        # Get model and app name for URLs
        self.model_name = model.__name__.lower() if model else ""
        self.app_label = model._meta.app_label if model else ""

        # Ensure key field is visible and positioned after actions
        if self.key_field not in self.visible_columns:
            self.visible_columns.insert(1, self.key_field)
        else:
            # Move key field to follow actions (position 1)
            self.visible_columns.remove(self.key_field)
            self.visible_columns.insert(1, self.key_field)

    def initialize_columns(self):
        """Initialize column model from serializer fields"""
        serializer_class = self.serializer_class or self.get_serializer_class()
        serializer_fields = serializer_class().get_fields()
        model = getattr(serializer_class.Meta, "model", None)
        form_elements = 0

        # Process each visible column
        for field_name in self.visible_columns:
            # Skip if already processed (actions column)
            if field_name == 'actions':
                continue

            # Base column configuration
            col_config = {
                "name": field_name,
                "index": field_name,
                "label": field_name.replace('_', ' ').title(),
                "editable": True,
                "required": False,
                "search": field_name in self.search_fields,
                "sortable": field_name in self.ordering_fields,  # Default based on ordering_fields
                "autoResizable": True
            }

            # Apply serializer field metadata
            field = serializer_fields.get(field_name)
            if field:
                # Read-only status
                if getattr(field, 'read_only', False):
                    col_config["editable"] = False

                # Required status
                if getattr(field, 'required', False):
                    col_config["required"] = True

                # Field label
                if hasattr(field, 'label') and field.label:
                    col_config["label"] = field.label
                elif field_name in self.header_titles:
                    col_config["label"] = self.header_titles[field_name]

            # Apply model field configuration
            if model:
                try:
                    model_field = model._meta.get_field(field_name)
                    field_type = model_field.__class__.__name__

                    # Apply field type configuration
                    if field_type in self.FIELD_TYPE_CONFIGS:
                        self._apply_field_type_config(col_config, model_field, field_type)

                    # Special handling for foreign keys
                    if hasattr(model_field, 'remote_field') and model_field.remote_field:
                        self._configure_relation_field(col_config, model_field)

                    # Handle choices
                    if hasattr(model_field, 'choices') and model_field.choices:
                        self._configure_choice_field(col_config, model_field.choices)

                    # If ID field, ensure it's not editable
                    if field_name == 'id' or getattr(model_field, 'primary_key', False):
                        col_config["editable"] = False
                        if field_name == self.key_field:
                            col_config["key"] = True
                            # Add formatter for ID field to match first code
                            col_config['formatter'] = 'open_button'

                except Exception as e:
                    # Silently handle fields that might be properties or derived
                    pass

            # Mark as groupable if in groupable_fields
            if field_name in self.groupable_fields:
                col_config["groupable"] = True

            # Apply any field overrides from viewset
            if field_name in self.jqgrid_field_overrides:
                col_config.update(self.jqgrid_field_overrides[field_name])

            # Add to column names list
            self.colnames.append(col_config.get("label", field_name.replace('_', ' ').title()))

            # Add form position information if editable
            if col_config["editable"]:
                col_config["formoptions"] = {
                    "colpos": (form_elements % 4) + 1,
                    "rowpos": (form_elements // 4) + 1
                }
                form_elements += 1

            # Add to column model
            self.colmodel.append(col_config)

    def _apply_field_type_config(self, col_config, model_field, field_type):
        """Apply configuration based on field type"""
        type_config = self.FIELD_TYPE_CONFIGS[field_type].copy()

        # Add search operations
        if 'search_ops' in type_config:
            col_config['search_ops'] = type_config['search_ops']

        # Handle sortable setting from field type - override default if specified
        if 'sortable' in type_config:
            # Field type config overrides the default ordering_fields logic
            col_config['sortable'] = type_config['sortable']

        # Apply remaining configuration
        for key, value in type_config.items():
            if key not in ['search_ops', 'search_init', 'needs_decimal_places', 'sortable']:
                col_config[key] = value

        # Special handling for decimal fields
        if type_config.get('needs_decimal_places', False):
            decimal_places = getattr(model_field, "decimal_places", 2)
            col_config["formatoptions"] = col_config.get("formatoptions", {})
            col_config["formatoptions"]["decimalPlaces"] = decimal_places

        # Add search options if field is searchable
        if col_config.get('search') and 'search_ops' in col_config:
            col_config['searchoptions'] = {
                'sopt': col_config['search_ops']
            }

    def _configure_relation_field(self, col_config, model_field):
        """Configure foreign key and related fields"""
        from django.db import models

        # Handle different relationship types
        if isinstance(model_field, models.ForeignKey):
            related_model = model_field.related_model
            related_name = related_model.__name__.lower()
            related_app = related_model._meta.app_label

            # Get field name without _id suffix if present
            field_name = model_field.name
            if field_name.endswith('_id'):
                field_name = field_name[:-3]

            # Configure dataUrl for dropdowns
            col_config.update({
                "stype": "select",
                "formatter": "select",
                "edittype": "select",
                "editoptions": {
                    "dataUrl": f"/api/{related_app}/{related_name}/dropdown/?field_name={field_name}&format=json",
                    "dataUrlTemp": f"/api/{related_app}/{related_name}/<id>/dropdown_pk/?field_name={field_name}&all=true&format=json",
                    "dataType": "application/json"
                },
                "addoptions": {
                    "dataUrl": f"/api/{related_app}/{related_name}/dropdown/?field_name={field_name}&format=json",
                    "dataUrlTemp": f"/api/{related_app}/{related_name}/<id>/dropdown_pk/?field_name={field_name}&all=true&format=json",
                    "dataType": "application/json"
                }
            })

            # Add search options if searchable
            if col_config.get("search", False):
                col_config["searchoptions"] = col_config.get("searchoptions", {})
                col_config["searchoptions"].update({
                    "dataUrl": f"/api/{related_app}/{related_name}/dropdown/?field_name={field_name}&format=json",
                    "dataUrlTemp": f"/api/{related_app}/{related_name}/<id>/dropdown-pk/?field_name={field_name}&all=true&format=json",
                    "dataType": "application/json"
                })
                # If search_ops isn't set, use eq/ne for select fields
                if "sopt" not in col_config["searchoptions"]:
                    col_config["searchoptions"]["sopt"] = ["eq", "ne"]

            # Foreign keys are typically read-only in the first code
            col_config["editable"] = False

    def _configure_choice_field(self, col_config, choices):
        """Configure choice fields as select dropdowns"""
        # Format choices for jqGrid
        choice_values = ":All;" + ";".join([f"{k}:{v}" for k, v in choices])

        # Set up select configuration
        col_config.update({
            "stype": "select",
            "formatter": "select",
            "edittype": "select",
            "editoptions": {"value": choice_values},
        })

        # Add search options if searchable
        if col_config.get("search", False):
            col_config["searchoptions"] = col_config.get("searchoptions", {})
            col_config["searchoptions"].update({
                "value": choice_values,
                "sopt": ["eq", "ne"]
            })

    def configure_grid_options(self):
        """Configure jqGrid main options"""
        # Start with default options from settings
        self.jqgrid_options = self.DEFAULT_GRID_OPTIONS.copy()

        # Get ordering from view if available
        ordering = getattr(self, 'ordering', None)
        sortname = ""
        sortorder = ""

        # Process ordering for multi-sort
        if ordering:
            if isinstance(ordering, (list, tuple)):
                # Convert ordering list to sortname,sortorder format
                sortfields = []
                sortdirections = []

                for field in ordering:
                    if field.startswith('-'):
                        sortfields.append(field[1:])  # Remove the minus sign
                        sortdirections.append('desc')
                    else:
                        sortfields.append(field)
                        sortdirections.append('asc')

                sortname = ",".join(sortfields)
                sortorder = ",".join(sortdirections)
            elif isinstance(ordering, str):
                # Single field ordering
                if ordering.startswith('-'):
                    sortname = ordering[1:]
                    sortorder = 'desc'
                else:
                    sortname = ordering
                    sortorder = 'asc'

        # Default to key_field if no ordering specified
        if not sortname:
            sortname = self.key_field
            sortorder = 'asc'

        # Update with dynamic values
        # Try to build URLs using Django's reverse, fallback to constructed URLs
        try:
            from django.urls import reverse
            # Try to reverse the list view URL using the model name
            list_url = reverse(f'{self.app_label}:{self.model_name}-list')
        except:
            # Fallback to constructed URL with pluralization
            # Most Django REST APIs use plural forms
            app_label_plural = self.app_label if self.app_label.endswith('s') else f"{self.app_label}s"
            model_name_plural = self.model_name if self.model_name.endswith('s') else f"{self.model_name}s"
            list_url = f"/{app_label_plural}/api/{model_name_plural}/"
        
        # Build CRUD URL
        crud_url = f"{list_url.rstrip('/')}/crud/"
        
        self.jqgrid_options.update({
            "url": list_url,
            "editurl": crud_url,
            "colModel": self.colmodel,
            "colNames": self.colnames,
            "sortname": sortname,
            "sortorder": sortorder,
            "multiSort": bool(isinstance(ordering, (list, tuple)) and len(ordering) > 1),
            "shrinkToFit": False,
            "caption": f"{self.model_name.replace('_', ' ').title()} Data",
        })

        # Rest of the method continues as before...

        # Ensure grid makes column names match column labels
        if "colNames" in self.jqgrid_options and len(self.jqgrid_options["colNames"]) != len(self.colmodel):
            # Rebuild colNames from colModel to ensure they match
            self.jqgrid_options["colNames"] = [col.get("label", col.get("name", "").replace("_", " ").title())
                                               for col in self.colmodel]

        # Update prmNames to match first code
        self.jqgrid_options["prmNames"] = {
            "page": "page",
            "rows": "rows",  # Changed from 'page_size' to 'rows' to match pagination
            "id": self.key_field,
            "order": "sord"
        }

        # Update jsonReader to match first code
        self.jqgrid_options["jsonReader"] = {
            "root": "rows",
            "page": "page",
            "total": "total",
            "records": "records",
            "id": self.key_field,
            "repeatitems": False
        }

        # Add rowList values to match first code
        self.jqgrid_options["rowList"] = [25, 50, 100, 500, 1000, 2000, 5000]

        # Apply any custom overrides defined in the viewset
        if hasattr(self, 'jqgrid_options_override'):
            self.jqgrid_options.update(self.jqgrid_options_override)

    def configure_method_options(self):
        """Configure method options for jqGrid"""
        # Start with default method options from settings
        self.method_options = self.DEFAULT_METHOD_OPTIONS.copy()

        # Update navGrid options to match first code
        self.method_options['navGrid']['options'].update({
            "edit": False,
            "add": False,
            "del": False,
            "search": True,
            "refresh": True,
            "view": False
        })

        # Customize edit caption if needed
        if 'navGrid' in self.method_options and 'editOptions' in self.method_options['navGrid']:
            self.method_options['navGrid']['editOptions']['editCaption'] = f"Edit {self.model_name.title()}"

        # Apply any custom overrides defined in the viewset
        if hasattr(self, 'method_options_override'):
            self._deep_update(self.method_options, self.method_options_override)

    def _deep_update(self, original, update):
        """Recursively update nested dictionaries"""
        for key, value in update.items():
            if key in original and isinstance(original[key], dict) and isinstance(value, dict):
                self._deep_update(original[key], value)
            else:
                original[key] = value

    def _configure_frozen_columns(self):
        """Configure frozen columns"""
        self.frozen_columns = getattr(self, 'frozen_columns', [])
        self.frozen_columns_enabled = bool(self.frozen_columns)

        if self.frozen_columns:
            for col in self.colmodel:
                if col.get('name') in self.frozen_columns:
                    col['frozen'] = True

    def _configure_grouping(self):
        """Configure grouping options"""
        self.groupable_fields = getattr(self, 'groupable_fields', [])

        if self.groupable_fields:
            default_group_field = self.groupable_fields[0]
            self.grouping_options = {
                "groupField": default_group_field,
                "groupColumnShow": [True],
                "groupText": ["<b>{0}</b>"],
                "groupOrder": ["asc"],
                "groupSummary": [True],
                "showSummaryOnHide": True
            }

    def _configure_conditional_formatting(self):
        """Configure conditional formatting"""
        self.conditional_formatting = getattr(self, 'conditional_formatting', {})
        if self.conditional_formatting:
            self.additional_data['conditional_formatting'] = self.conditional_formatting

    def _configure_highlight_rules(self):
        """Configure row highlighting rules"""
        self.highlight_rules = getattr(self, 'highlight_rules', {})
        if self.highlight_rules:
            self.additional_data['highlight_rules'] = self.highlight_rules

    def _configure_bulk_actions(self):
        """Configure bulk actions"""
        # Define which fields can be bulk updated
        serializer_class = self.serializer_class or self.get_serializer_class()
        model = getattr(serializer_class.Meta, "model", None)
        serializer_fields = serializer_class().get_fields()
        self.bulk_updateable_fields = getattr(self, 'bulk_updateable_fields', [])

        # If no specific fields are defined, auto-generate from column model
        if not self.bulk_updateable_fields:
            for field_name in self.visible_columns:
                # Skip id and non-editable fields
                if field_name in ['id', 'actions', 'cb', 'rn']:
                    continue

                # Check if field is editable in serializer
                field = serializer_fields.get(field_name)
                if field and not getattr(field, 'read_only', False):
                    self.bulk_updateable_fields.append(field_name)

        # Define default bulk actions
        self.bulk_actions = getattr(self, 'bulk_actions', [
            {
                'id': 'bulk-delete',
                'label': 'Delete Selected',
                'icon': 'fa-trash',
                'class': 'btn-danger'
            },
            {
                'id': 'bulk-update',
                'label': 'Update Selected',
                'icon': 'fa-edit',
                'class': 'btn-primary'
            }
        ])

        # Set bulk action config
        self.bulk_action_config = {
            'actions': self.bulk_actions,
            'updateableFields': self.bulk_updateable_fields
        }

    def get_tmplgilters(self):
        """Get template filters for search options"""
        from django_jqgrid.models import GridFilter
        try:
            # Get content type with caching
            content_type = get_content_type_cached(
                self.queryset.model._meta.app_label,
                self.queryset.model._meta.model_name
            )
            
            if not content_type:
                return {"tmplNames": [], "tmplFilters": [], "tmplIds": []}
            
            # Get user-specific filters
            user_filters = GridFilter.objects.filter(
                key='tmplFilters',
                table=content_type,
                created_by=self.request.user,
                is_global=False
            ).values('id', 'name', 'value')

            # Get global filters
            global_filters = GridFilter.objects.filter(
                key='tmplFilters',
                table=content_type,
                is_global=True
            ).values('id', 'name', 'value')

            # Combine user and global filters
            data = list(user_filters) + list(global_filters)

            tmplNames = []
            tmplIds = []
            tmplFilters = []
            for i in data:
                tmplIds.append(i['id'])
                tmplNames.append(i['name'])
                tmplFilters.append(i['value'])
            return {"tmplNames": tmplNames, "tmplFilters": tmplFilters, "tmplIds": tmplIds}
        except Exception as e:
            import logging
            logging.error(f"Error getting template filters: {e}")
            return {"tmplNames": [], "tmplFilters": [], "tmplIds": []}

    @action(methods=['get'], detail=False)
    def jqgrid_config(self, request, *args, **kwargs):
        """Return jqGrid configuration in compatible format"""
        self.initgrid()

        response_data = {
            'jqgrid_options': self.jqgrid_options,
            'method_options': {
                'navGrid': {
                    'selector': '#jqGridPager',
                    'options': self.method_options.get('navGrid', {}).get('options', {}),
                    'editOptions': self.method_options.get('navGrid', {}).get('editOptions', {}),
                    'addOptions': self.method_options.get('navGrid', {}).get('addOptions', {}),
                    'delOptions': self.method_options.get('navGrid', {}).get('delOptions', {}),
                    'searchOptions': self.method_options.get('navGrid', {}).get('searchOptions', {}),
                    'viewOptions': self.method_options.get('navGrid', {}).get('viewOptions', {})
                },
                'filterToolbar': {'options': self.method_options.get('filterToolbar', {}).get('options', {})}
            }
        }

        # Add conditional groupingGroupBy method option if grouping is enabled
        if hasattr(self, 'grouping_options') and self.grouping_options:
            response_data['method_options']['groupingGroupBy'] = {'options': self.grouping_options}

        # Add bulk_action_config
        if hasattr(self, 'bulk_action_config'):
            response_data['bulk_action_config'] = self.bulk_action_config

        # Add header_titles
        if hasattr(self, 'header_titles'):
            response_data['header_titles'] = self.header_titles

        # Add additional data if available
        if hasattr(self, 'additional_data'):
            for key, value in self.additional_data.items():
                if key not in response_data:
                    response_data[key] = value

        return Response(response_data)

    @action(methods=['post'], detail=False, url_path='crud')
    def crud(self, request, *args, **kwargs):
        """Handle CRUD operations via jqGrid"""
        oper = request.data.get("oper")
        record_id = request.data.get("id")

        if oper == "add":
            request.method = "POST"
            return self.create(request, *args, **kwargs)
        elif oper == "edit" and record_id:
            request.method = "PUT"
            self.kwargs["pk"] = record_id
            return self.update(request, *args, **kwargs)
        elif oper == "del" and record_id:
            request.method = "DELETE"
            self.kwargs["pk"] = record_id
            return self.destroy(request, *args, **kwargs)

        return Response({"success": False, "message": "Invalid operation"}, status=400)

    def generate_filter_mappings(self):
        """Generate filter mappings for jqGrid search toolbox"""
        filter_mappings = {}
        standard_mappings = {
            "eq": "", "ne": "__ne", "lt": "__lt", "le": "__lte", "gt": "__gt", "ge": "__gte",
            "cn": "__icontains", "nc": "__icontains", "bw": "__istartswith", "bn": "__istartswith",
            "ew": "__iendswith", "en": "__iendswith", "in": "__in", "ni": "__in",
            "nu": "__isnull", "nn": "__isnull"
        }

        # Create mappings for each field and operator
        for field_name in self.search_fields:
            for op, lookup in standard_mappings.items():
                filter_mappings[f"{field_name}__jq_{op}"] = f"{field_name}{lookup}"

        return filter_mappings


from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ValidationError
from django.db import transaction
import logging

logger = logging.getLogger(__name__)


class JqGridBulkActionMixin:
    """
    Refactored mixin for handling jqGrid-compatible bulk actions (update/delete),
    based purely on the serializer and optional per-view field controls.
    """

    # Optional per-view override: limit fields that can be bulk updated
    allowed_bulk_fields = []

    def get_bulk_queryset(self, ids):
        """
        Return queryset filtered by IDs (safe lookup)
        """
        try:
            return self.get_queryset().filter(id__in=ids)
        except Exception as e:
            logger.error(f"Error filtering bulk queryset: {e}")
            return self.get_queryset().none()

    def get_bulk_editable_fields(self):
        """
        Get allowed fields for bulk update from serializer (or override via `allowed_bulk_fields`)
        """
        serializer_class = self.serializer_class or self.get_serializer_class()
        serializer = serializer_class()
        all_fields = serializer.get_fields()
        editable_fields = [
            name for name, field in all_fields.items()
            if not field.read_only
        ]
        if self.allowed_bulk_fields:
            return [f for f in self.allowed_bulk_fields if f in editable_fields]
        return editable_fields

    def validate_bulk_data(self, data):
        """
        Validate the structure and field-level safety of incoming bulk request.
        """
        if not isinstance(data, dict):
            raise ValidationError("Invalid payload format.")

        ids = data.get("ids", [])
        action_data = data.get("action", {})

        if not isinstance(ids, list) or not ids:
            raise ValidationError("No valid IDs provided.")

        if not isinstance(action_data, dict):
            raise ValidationError("Invalid action data format.")

        if "_delete" in action_data:
            if not isinstance(action_data["_delete"], bool):
                raise ValidationError("`_delete` must be a boolean.")

        return ids, action_data

    def process_bulk_update(self, objs, updates):
        """
        Process bulk update (default version) — override for custom logic.
        """
        updated_count = 0
        for obj in objs:
            for key, val in updates.items():
                setattr(obj, key, val)
            obj.save()
            updated_count += 1
        return {"updated": updated_count}

    @action(methods=['post'], detail=False)
    def bulk_action(self, request):
        """
        Endpoint to handle bulk update/delete via jqGrid.

        Payload:
        {
            "ids": [1, 2, 3],
            "action": {
                "field1": "value",
                "field2": "value",
                ...
            }
        }

        For deletion:
        {
            "ids": [1, 2, 3],
            "action": {
                "_delete": true
            }
        }
        """
        try:
            ids, action_data = self.validate_bulk_data(request.data)

            is_delete = action_data.get("_delete", False)
            queryset = self.get_bulk_queryset(ids)

            if not queryset.exists():
                return Response({
                    "status": "error",
                    "message": "No matching records found."
                }, status=status.HTTP_404_NOT_FOUND)

            if is_delete:
                deleted_count = queryset.delete()[0]
                return Response({
                    "status": "success",
                    "message": f"Deleted {deleted_count} records.",
                    "deleted_ids": ids
                })

            # Validate editable fields
            allowed_fields = self.get_bulk_editable_fields()
            invalid_fields = [k for k in action_data.keys() if k not in allowed_fields]
            if invalid_fields:
                return Response({
                    "status": "error",
                    "message": f"Fields not allowed for bulk update: {invalid_fields}"
                }, status=status.HTTP_400_BAD_REQUEST)

            # Proceed with update
            with transaction.atomic():
                result = self.process_bulk_update(queryset, action_data)

            return Response({
                "status": "success",
                "message": f"Updated {queryset.count()} records.",
                "results": result,
                "updated_ids": ids
            })

        except ValidationError as e:
            return Response({"status": "error", "message": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            logger.exception("Bulk action error")
            return Response({
                "status": "error",
                "message": "An unexpected error occurred."
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
