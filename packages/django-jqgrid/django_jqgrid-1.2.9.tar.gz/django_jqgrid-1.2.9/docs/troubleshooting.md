# Troubleshooting Guide

This guide covers common issues with django-jqgrid and their solutions.

## Table of Contents
1. [Common django-jqgrid Issues](#common-django-jqgrid-issues)
2. [PyPI Upload Errors](#pypi-upload-errors)

## Common django-jqgrid Issues

### 1. Grid Not Loading / Blank Grid

**Symptoms:**
- Grid container appears but no data is shown
- No errors in console but grid is empty

**Solutions:**
```javascript
// Check if jQuery is loaded before jqGrid
if (typeof jQuery === 'undefined') {
    console.error('jQuery is not loaded');
}

// Ensure correct initialization order
$(document).ready(function() {
    // Load configuration first
    $.getJSON('/api/yourapp/yourmodel/jqgrid_config/', function(config) {
        $("#jqGrid").jqGrid(config.jqgrid_options);
    });
});
```

**Common Causes:**
- jQuery not loaded or loaded after jqGrid
- Incorrect API endpoint URL
- Missing CSRF token for POST requests
- ViewSet not properly configured with mixins

### 2. 403 Forbidden Error on CRUD Operations

**Symptoms:**
```
POST /api/model/crud/ 403 Forbidden
CSRF token missing or incorrect
```

**Solutions:**
```javascript
// Add CSRF token to all AJAX requests
$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!(/^(GET|HEAD|OPTIONS|TRACE)$/.test(settings.type)) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
        }
    }
});

// Or add to jqGrid configuration
$("#jqGrid").jqGrid({
    // ... other options ...
    ajaxGridOptions: {
        headers: {
            'X-CSRFToken': getCookie('csrftoken')
        }
    }
});
```

### 3. Foreign Key Dropdowns Not Showing

**Symptoms:**
- Select dropdowns for foreign keys are empty
- Console shows 404 for dropdown endpoint

**Solutions:**
```python
# Ensure ViewSet has proper dropdown method
class YourModelViewSet(JqGridConfigMixin, viewsets.ModelViewSet):
    # ... other configuration ...
    
    @action(detail=False, methods=['get'])
    def dropdown(self, request):
        # This is handled by the mixin, just ensure it's accessible
        return super().dropdown(request)
```

**Check URL configuration:**
```python
# urls.py
router = routers.DefaultRouter()
router.register(r'yourmodel', YourModelViewSet)
urlpatterns = [
    path('api/', include(router.urls)),
]
```

### 4. Date Filtering Not Working

**Symptoms:**
- Date filters return no results
- Dates display incorrectly in grid

**Solutions:**
```python
# In your serializer, ensure proper date formatting
class YourSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S')
    
    class Meta:
        model = YourModel
        fields = '__all__'
```

```javascript
// In jqGrid configuration
colModel: [{
    name: 'created_at',
    index: 'created_at',
    formatter: 'date',
    formatoptions: {
        srcformat: 'Y-m-d H:i:s',
        newformat: 'm/d/Y'
    },
    searchoptions: {
        dataInit: function(elem) {
            $(elem).datepicker({
                dateFormat: 'yy-mm-dd'
            });
        }
    }
}]
```

### 5. Bulk Operations Not Working

**Symptoms:**
- Bulk update/delete buttons don't appear
- Bulk actions return 400 Bad Request

**Solutions:**
```python
# Ensure ViewSet includes bulk action mixin
class YourModelViewSet(JqGridConfigMixin, JqGridBulkActionMixin, viewsets.ModelViewSet):
    # Define which fields can be bulk updated
    bulk_updateable_fields = ['status', 'category', 'price']
    
    # Ensure user has permissions
    def get_permissions(self):
        if self.action in ['bulk_action']:
            return [IsAuthenticated(), DjangoModelPermissions()]
        return super().get_permissions()
```

### 6. Grid Columns Not Aligned / CSS Issues

**Symptoms:**
- Headers and data columns misaligned
- Grid looks broken visually

**Solutions:**
```html
<!-- Ensure correct CSS loading order -->
<link rel="stylesheet" href="{% static 'django_jqgrid/plugins/jqGrid/css/ui.jqgrid-bootstrap4.css' %}">
<!-- Load after Bootstrap CSS -->
<link rel="stylesheet" href="{% static 'django_jqgrid/css/jqgrid-bootstrap.css' %}">

<script>
// Force grid resize after loading
$(window).on('load resize', function() {
    $("#jqGrid").jqGrid('setGridWidth', $(".grid-container").width());
});
</script>
```

### 7. Search/Filter Not Returning Results

**Symptoms:**
- Search box doesn't filter data
- Advanced search returns empty results

**Solutions:**
```python
# Ensure search fields are defined
class YourModelViewSet(JqGridConfigMixin, viewsets.ModelViewSet):
    search_fields = ['name', 'description', 'email']
    filterset_fields = ['status', 'category', 'created_at']
    
    # For complex filtering
    def get_queryset(self):
        queryset = super().get_queryset()
        # Add any custom filtering logic
        return queryset
```

### 8. Performance Issues with Large Datasets

**Symptoms:**
- Grid loads slowly with many records
- Browser becomes unresponsive

**Solutions:**
```python
# Optimize queryset with select_related/prefetch_related
class YourModelViewSet(JqGridConfigMixin, viewsets.ModelViewSet):
    def get_queryset(self):
        return YourModel.objects.select_related(
            'category', 'user'
        ).prefetch_related(
            'tags', 'comments'
        )
    
    # Enable server-side pagination
    pagination_class = JqGridPagination
```

```javascript
// Enable virtual scrolling for large datasets
$("#jqGrid").jqGrid({
    scroll: 1,
    rowNum: 50,
    viewrecords: true,
    loadonce: false  // Keep server-side processing
});
```

### 9. Custom Actions Not Working

**Symptoms:**
- Custom buttons don't trigger actions
- Custom formatter functions not called

**Solutions:**
```javascript
// Define custom formatters globally
$.extend($.fn.fmatter, {
    customAction: function(cellval, opts, rwd) {
        return '<button onclick="handleCustomAction(' + opts.rowId + ')">Action</button>';
    }
});

// Add custom buttons to toolbar
$("#jqGrid").jqGrid('navButtonAdd', '#jqGridPager', {
    caption: "Custom",
    buttonicon: "fa-cog",
    onClickButton: function() {
        // Custom action code
    },
    position: "last"
});
```

### 10. Import/Export Features Not Working

**Symptoms:**
- Export button doesn't download file
- Import fails with validation errors

**Solutions:**
```python
# Configure import/export in ViewSet
class YourModelViewSet(JqGridConfigMixin, viewsets.ModelViewSet):
    # Export configuration
    export_config = {
        'formats': ['csv', 'xlsx'],
        'include_headers': True,
        'max_rows': 10000
    }
    
    # Import configuration
    import_config = {
        'supported_formats': ['csv', 'xlsx'],
        'field_mapping': {
            'Product Name': 'name',  # CSV header -> model field
            'Price': 'price'
        }
    }
```

### 11. Permission-Based Column Visibility

**Symptoms:**
- All columns visible regardless of permissions
- Sensitive data exposed to unauthorized users

**Solutions:**
```python
class YourModelViewSet(JqGridConfigMixin, viewsets.ModelViewSet):
    def get_visible_columns(self):
        """Override to implement permission-based visibility"""
        base_columns = ['id', 'name', 'created_at']
        
        if self.request.user.has_perm('app.view_sensitive_data'):
            base_columns.extend(['salary', 'ssn', 'phone'])
            
        return base_columns
```

### 12. Timezone Issues

**Symptoms:**
- Dates show wrong time
- Filtering by date gives unexpected results

**Solutions:**
```python
# settings.py
USE_TZ = True
TIME_ZONE = 'America/New_York'

# In serializer
class YourSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(
        format='%Y-%m-%d %H:%M:%S %Z',
        default_timezone=pytz.timezone('America/New_York')
    )
```

## Debugging Tips

### Enable Debug Mode
```javascript
// Add debug parameter to see raw responses
$("#jqGrid").jqGrid({
    // ... options ...
    loadError: function(xhr, status, error) {
        console.error('Load error:', status, error);
        console.error('Response:', xhr.responseText);
    }
});
```

### Check Network Requests
1. Open browser Developer Tools (F12)
2. Go to Network tab
3. Look for failed requests (red)
4. Check request/response headers and body

### Common Debug Commands
```python
# Django shell debugging
python manage.py shell
>>> from yourapp.models import YourModel
>>> from yourapp.serializers import YourSerializer
>>> obj = YourModel.objects.first()
>>> serializer = YourSerializer(obj)
>>> print(serializer.data)  # Check serialization

# Check permissions
>>> from django.contrib.auth.models import User
>>> user = User.objects.get(username='testuser')
>>> user.has_perm('yourapp.change_yourmodel')
```

## PyPI Upload Errors

## Common `twine upload` Errors and Solutions

### 1. **Error: The credentials were not found or were invalid**

**Symptoms:**
```
HTTPError: 403 Forbidden from https://upload.pypi.org/legacy/
Invalid or non-existent authentication information.
```

**Solutions:**
- Ensure you're using an API token, not username/password
- Check token format: should start with `pypi-`
- Verify token is in `.pypi_tokens.conf`
- For Windows, check token doesn't have extra spaces or line breaks

**Fix:**
```cmd
# Windows
set TWINE_USERNAME=__token__
set TWINE_PASSWORD=pypi-YOUR-TOKEN-HERE
python -m twine upload dist/*
```

### 2. **Error: HTTPError: 400 Bad Request**

**Symptoms:**
```
HTTPError: 400 Bad Request from https://upload.pypi.org/legacy/
Invalid distribution file
```

**Solutions:**
- Run `python -m twine check dist/*`
- Rebuild the package: `python -m build --wheel --sdist`
- Check for invalid characters in package metadata

### 3. **Error: Package already exists**

**Symptoms:**
```
HTTPError: 400 Bad Request from https://upload.pypi.org/legacy/
File already exists
```

**Solutions:**
- You can't upload the same version twice
- Bump the version: `publish.bat -b patch`
- Delete old files from `dist/` folder

### 4. **Error: SSL Certificate verification failed**

**Symptoms:**
```
SSL: CERTIFICATE_VERIFY_FAILED
```

**Solutions for Windows:**
```cmd
# Update certificates
pip install --upgrade certifi

# Or disable SSL verification (NOT recommended for production)
set TWINE_CERT=/path/to/cert.pem
```

### 5. **Error: Connection timeout**

**Symptoms:**
```
requests.exceptions.ConnectTimeout
```

**Solutions:**
- Check internet connection
- Check proxy settings
- Try using a different network
- For corporate networks:
  ```cmd
  set HTTP_PROXY=http://proxy.company.com:8080
  set HTTPS_PROXY=http://proxy.company.com:8080
  ```

### 6. **Error: Invalid token format**

**Symptoms:**
```
HTTPError: 401 Unauthorized
```

**Solutions:**
- Ensure token starts with `pypi-`
- No extra spaces or quotes around token
- Token hasn't expired
- Using correct token for correct repository (PyPI vs TestPyPI)

## Debug Commands for Windows

### 1. Test with verbose output:
```cmd
python -m twine upload --verbose --repository testpypi dist/*
```

### 2. Check package validity:
```cmd
python -m twine check dist/*
```

### 3. Manual upload with token:
```cmd
# Set environment variables
set TWINE_USERNAME=__token__
set TWINE_PASSWORD=pypi-AgEIcHlwaS5vcmcCJGI0MjcxY2QtMzcyYS00YTJmLThh...

# Upload
python -m twine upload --repository testpypi dist/*
```

### 4. Test with config file:
```cmd
# Create .pypirc in user home directory
echo [distutils] > %USERPROFILE%\.pypirc
echo index-servers = >> %USERPROFILE%\.pypirc
echo     pypi >> %USERPROFILE%\.pypirc
echo     testpypi >> %USERPROFILE%\.pypirc
echo. >> %USERPROFILE%\.pypirc
echo [pypi] >> %USERPROFILE%\.pypirc
echo username = __token__ >> %USERPROFILE%\.pypirc
echo password = pypi-YOUR-TOKEN-HERE >> %USERPROFILE%\.pypirc
echo. >> %USERPROFILE%\.pypirc
echo [testpypi] >> %USERPROFILE%\.pypirc
echo repository = https://test.pypi.org/legacy/ >> %USERPROFILE%\.pypirc
echo username = __token__ >> %USERPROFILE%\.pypirc
echo password = pypi-YOUR-TEST-TOKEN-HERE >> %USERPROFILE%\.pypirc
```

### 5. Run debug script:
```cmd
# Use the debug script
python debug_upload.py

# Or on Windows
debug_upload.bat
```

## Quick Checklist

Before uploading, ensure:

1. ✓ Package builds without errors: `python -m build`
2. ✓ Package passes checks: `python -m twine check dist/*`
3. ✓ Token is correctly formatted (starts with `pypi-`)
4. ✓ Using `__token__` as username
5. ✓ No old versions in `dist/` folder
6. ✓ Version number is unique
7. ✓ Internet connection is working
8. ✓ Using correct repository URL

## Getting More Help

If you still have issues:

1. Run the debug script: `python debug_upload.py`
2. Check PyPI status: https://status.python.org/
3. Try TestPyPI first: https://test.pypi.org/
4. Check token permissions on PyPI website
5. Create a new token if needed

## Example Successful Upload

Here's what a successful upload looks like:

```
Uploading distributions to https://upload.pypi.org/legacy/
Uploading django_jqgrid-1.0.0-py3-none-any.whl
100%|████████████████████| 1.20M/1.20M [00:02<00:00, 564kB/s]
Uploading django_jqgrid-1.0.0.tar.gz
100%|████████████████████| 1.06M/1.06M [00:01<00:00, 612kB/s]

View at:
https://pypi.org/project/django-jqgrid/1.0.0/
```