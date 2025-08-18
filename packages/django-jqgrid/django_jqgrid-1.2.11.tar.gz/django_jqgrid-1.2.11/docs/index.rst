Django jqGrid Documentation
===========================

Welcome to Django jqGrid's documentation!

Django jqGrid is a comprehensive Django package that integrates jqGrid with Django REST Framework. It provides automatic grid configuration based on Django models and serializers, making it easy to create feature-rich data grids with minimal code.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   installation
   quickstart
   configuration
   api_reference
   troubleshooting
   contributing
   changelog

Features
--------

* **Automatic Configuration**: Grid configuration is automatically generated from Django models and DRF serializers
* **Full CRUD Operations**: Create, read, update, and delete operations with permission handling
* **Advanced Filtering**: Built-in search, filters, and custom user-defined filters
* **Bulk Operations**: Perform operations on multiple rows simultaneously
* **Real-time Updates**: Support for real-time grid updates via WebSockets
* **Bootstrap Integration**: Seamless integration with Bootstrap 4 and 5
* **Responsive Design**: Mobile-friendly responsive grid layouts
* **Internationalization**: Multi-language support with extensive locale options
* **Custom Formatting**: Conditional formatting and custom cell renderers
* **Export Capabilities**: Export grid data to various formats

Quick Start
-----------

1. Install Django jqGrid:

   .. code-block:: bash

      pip install django-jqgrid

2. Add to your Django settings:

   .. code-block:: python

      INSTALLED_APPS = [
          ...
          'rest_framework',
          'django_jqgrid',
      ]

3. Create a ViewSet with jqGrid integration:

   .. code-block:: python

      from django_jqgrid.mixins import JqGridConfigMixin
      from rest_framework import viewsets

      class ProductViewSet(JqGridConfigMixin, viewsets.ModelViewSet):
          queryset = Product.objects.all()
          serializer_class = ProductSerializer
          
          # Grid configuration
          visible_columns = ['id', 'name', 'price']
          search_fields = ['name', 'description']
          ordering_fields = ['name', 'price', 'created_at']

4. Include the URLs and render the grid in your template:

   .. code-block:: html

      {% load jqgrid_tags %}
      {% jqgrid_table 'products' %}

Getting Help
------------

* **GitHub**: https://github.com/django-jqgrid/django-jqgrid
* **Issues**: https://github.com/django-jqgrid/django-jqgrid/issues
* **Documentation**: https://django-jqgrid.readthedocs.io/

Requirements
------------

* Python 3.8+
* Django 3.2+
* Django REST Framework 3.12+
* jQuery 3.6+

Supported Versions
------------------

* Django: 3.2, 4.0, 4.1, 4.2, 5.0
* Django REST Framework: 3.12+
* Python: 3.8, 3.9, 3.10, 3.11, 3.12

License
-------

This project is licensed under the MIT License - see the LICENSE file for details.

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`