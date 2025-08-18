# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys
import django

sys.path.insert(0, os.path.abspath('..'))
sys.path.insert(0, os.path.abspath('../django_jqgrid'))

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'docs.settings')
try:
    django.setup()
except Exception:
    # Django setup might fail in Read the Docs environment
    pass

# -- Project information -----------------------------------------------------

project = 'Django jqGrid'
copyright = '2025, Django jqGrid Team'
author = 'Django jqGrid Team'

# The full version, including alpha/beta/rc tags
release = '1.2.3'
version = '1.2.3'

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    'sphinx.ext.napoleon',
    'sphinx.ext.intersphinx',
    'sphinx.ext.coverage',
    'sphinx.ext.githubpages',
]

# Add MyST parser if available
try:
    import myst_parser
    extensions.append('myst_parser')
except ImportError:
    print("MyST parser not available, using only RST files")

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# The suffix(es) of source filenames.
source_suffix = ['.rst', '.md']

# The master toctree document.
master_doc = 'index'

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
html_theme = 'sphinx_rtd_theme'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = []  # Empty for now, since _static doesn't exist

# Custom sidebar templates, must be a dictionary that maps document names
# to template names.
html_sidebars = {
    '**': [
        'relations.html',
        'searchbox.html',
    ]
}

# -- Options for autodoc extension -------------------------------------------

# This value selects if automatically documented members are sorted alphabetical (value 'alphabetical'), by member type (value 'groupwise') or by source order (value 'bysource').
autodoc_member_order = 'bysource'

# This value controls how to represent typehints.
autodoc_typehints = 'description'

# -- Options for intersphinx extension ---------------------------------------

# Example configuration for intersphinx: refer to the Python standard library.
intersphinx_mapping = {
    'python': ('https://docs.python.org/3/', None),
    'django': ('https://docs.djangoproject.com/en/stable/', 'https://docs.djangoproject.com/en/stable/_objects/'),
    # DRF doesn't provide intersphinx inventory
}

# -- Options for Napoleon extension ------------------------------------------

napoleon_google_docstring = True
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = False
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_examples = False
napoleon_use_admonition_for_notes = False
napoleon_use_admonition_for_references = False
napoleon_use_ivar = False
napoleon_use_param = True
napoleon_use_rtype = True

# -- Options for MyST parser -------------------------------------------------

# Only configure MyST if it's available
if 'myst_parser' in extensions:
    myst_enable_extensions = [
        "colon_fence",
        "deflist",
        "dollarmath",
        "fieldlist",
        "html_admonition",
        "html_image",
        "replacements",
        "smartquotes",
        "strikethrough",
        "substitution",
        "tasklist",
    ]
    
    # Only enable linkify if linkify-it-py is available
    try:
        import linkify_it
        myst_enable_extensions.append("linkify")
    except ImportError:
        pass
    
    myst_heading_anchors = 3