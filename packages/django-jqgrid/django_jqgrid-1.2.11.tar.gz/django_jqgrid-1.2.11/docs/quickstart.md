# Quick Start Guide

This guide will help you get started with Django jqGrid quickly.

## Prerequisites

- Python 3.8+
- Django 3.2+
- Django REST Framework 3.12+
- jQuery 3.6+

## Installation

```bash
pip install django-jqgrid
```

## Basic Setup

### 1. Add to Django Settings

Add `django_jqgrid` to your `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    ...
    'rest_framework',
    'django_jqgrid',
]

# Configure Django REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'django_jqgrid.pagination.OptimizedPaginator',
    'PAGE_SIZE': 20,
}
```

### 2. Include URLs

Add jqGrid URLs to your project:

```python
# urls.py
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('django_jqgrid.urls')),
    # your other URLs
]
```

### 3. Create a Model

```python
# models.py
from django.db import models

class Product(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name
```

### 4. Create a Serializer

```python
# serializers.py
from rest_framework import serializers
from .models import Product

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'
```

### 5. Create a ViewSet

```python
# views.py
from django_jqgrid.mixins import JqGridConfigMixin, JqGridBulkActionMixin
from rest_framework import viewsets
from .models import Product
from .serializers import ProductSerializer

class ProductViewSet(JqGridConfigMixin, JqGridBulkActionMixin, viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    
    # Grid configuration
    visible_columns = ['id', 'name', 'price', 'created_at', 'is_active']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'price', 'created_at']
    
    # Bulk operations
    bulk_updateable_fields = ['price', 'is_active']
```

### 6. Register URLs

```python
# urls.py (in your app)
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductViewSet

router = DefaultRouter()
router.register(r'products', ProductViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
]
```

### 7. Create a Template

```html
<!-- templates/products.html -->
<!DOCTYPE html>
<html>
<head>
    <title>Product Grid</title>
    {% load static %}
    {% load jqgrid_tags %}
    
    <!-- Bootstrap CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    
    <!-- jqGrid CSS -->
    {% jqgrid_css %}
</head>
<body>
    <div class="container mt-4">
        <h1>Product Management</h1>
        
        <!-- Grid Container -->
        {% jqgrid_table 'products' %}
    </div>
    
    <!-- jQuery -->
    <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
    
    <!-- Bootstrap JS -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    
    <!-- jqGrid JS -->
    {% jqgrid_js %}
</body>
</html>
```

### 8. Create a View

```python
# views.py (add this to your existing views)
from django.shortcuts import render

def product_grid(request):
    return render(request, 'products.html')
```

### 9. Add URL Pattern

```python
# urls.py (add this to your app URLs)
urlpatterns = [
    path('api/', include(router.urls)),
    path('products/', product_grid, name='product_grid'),
]
```

## Run the Application

1. Run migrations:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

2. Create a superuser:
   ```bash
   python manage.py createsuperuser
   ```

3. Start the development server:
   ```bash
   python manage.py runserver
   ```

4. Visit `http://localhost:8000/products/` to see your grid!

## Next Steps

- Check out the [Configuration Guide](configuration.md) for advanced options
- See the [API Reference](api_reference.md) for detailed documentation
- Look at the [Troubleshooting Guide](troubleshooting.md) if you encounter issues

## Common Patterns

### Custom Grid Configuration

```python
class ProductViewSet(JqGridConfigMixin, viewsets.ModelViewSet):
    # ... other configuration ...
    
    def get_jqgrid_config(self, request):
        config = super().get_jqgrid_config(request)
        
        # Customize grid options
        config['jqgrid_options'].update({
            'rowNum': 50,
            'sortname': 'name',
            'sortorder': 'asc',
            'caption': 'Product Catalog',
            'height': 400,
        })
        
        return config
```

### Adding Custom Actions

```python
from rest_framework.decorators import action
from rest_framework.response import Response

class ProductViewSet(JqGridConfigMixin, viewsets.ModelViewSet):
    # ... other configuration ...
    
    @action(detail=False, methods=['post'])
    def bulk_activate(self, request):
        """Activate selected products"""
        ids = request.data.get('ids', [])
        updated = self.queryset.filter(id__in=ids).update(is_active=True)
        return Response({'updated': updated})
```

You now have a fully functional jqGrid integrated with Django! The grid supports:
- CRUD operations
- Searching and filtering
- Sorting
- Pagination
- Bulk operations
- Responsive design