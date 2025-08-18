# jqGrid Ordering/Sorting Fix

## Problem

The ordering was not working because:
1. jqGrid sends sorting parameters as `sidx` (sort index/field) and `sord` (sort order)
2. Django REST Framework's `OrderingFilter` expects an `ordering` parameter
3. There was a mismatch between what jqGrid sends and what DRF expects

## Solution

Created `JqGridOrderingFilter` that:
1. Extends DRF's `OrderingFilter`
2. Intercepts jqGrid's `sidx`/`sord` parameters
3. Converts them to DRF's expected format
4. Maintains backward compatibility with standard `ordering` parameter

## Implementation

### 1. New Ordering Filter (`django_jqgrid/ordering.py`)

```python
from django_jqgrid import JqGridOrderingFilter

class ProductViewSet(viewsets.ModelViewSet):
    filter_backends = [JqGridFilterBackend, JqGridOrderingFilter]  # Use JqGridOrderingFilter
    ordering_fields = ['name', 'price', 'created_at']
    ordering = ['-created_at']  # Default ordering
```

### 2. Features

- **Single column sort**: `sidx=name&sord=asc`
- **Multi-column sort**: `sidx=status,price&sord=asc,desc`
- **Backward compatible**: `ordering=-created_at` still works
- **Field validation**: Only allows fields in `ordering_fields`
- **Related field support**: Handles `__` lookups with distinct()

### 3. Parameter Mapping

| jqGrid Parameters | DRF Equivalent | Example |
|-------------------|----------------|---------|
| `sidx=name&sord=asc` | `ordering=name` | Sort by name ascending |
| `sidx=price&sord=desc` | `ordering=-price` | Sort by price descending |
| `sidx=status,price&sord=asc,desc` | `ordering=status,-price` | Multi-column sort |

## Usage

### Basic Setup

```python
from django_jqgrid import JqGridOrderingFilter

class MyViewSet(viewsets.ModelViewSet):
    queryset = MyModel.objects.all()
    serializer_class = MySerializer
    
    # Use JqGridOrderingFilter instead of OrderingFilter
    filter_backends = [JqGridFilterBackend, JqGridOrderingFilter]
    
    # Define which fields can be sorted
    ordering_fields = ['name', 'price', 'created_at', 'status']
    
    # Default ordering (optional)
    ordering = ['-created_at']
```

### Advanced Usage

```python
# Sort on related fields
ordering_fields = ['name', 'category__name', 'created_by__username']

# All fields sortable (use with caution)
ordering_fields = '__all__'

# Custom field mapping
ordering_fields = {
    'display_name': 'name',  # Frontend field -> Model field
    'total': 'order_total',
}
```

## Testing

Run the test script to verify ordering works:

```bash
cd example_project
python manage.py runserver

# In another terminal
python test_ordering_fix.py
```

## Migration Guide

### Before (Not Working)
```python
from rest_framework.filters import OrderingFilter

class ProductViewSet(viewsets.ModelViewSet):
    filter_backends = [JqGridFilterBackend, OrderingFilter]  # OrderingFilter doesn't understand sidx/sord
```

### After (Working)
```python
from django_jqgrid import JqGridOrderingFilter

class ProductViewSet(viewsets.ModelViewSet):
    filter_backends = [JqGridFilterBackend, JqGridOrderingFilter]  # Now handles jqGrid parameters
```

## Client-Side (No Changes Needed)

jqGrid will continue to send standard parameters:
```javascript
$("#grid").jqGrid({
    url: '/api/products/',
    sortname: 'name',     // Becomes sidx parameter
    sortorder: 'asc',     // Becomes sord parameter
    // ... rest of config
});
```

## Troubleshooting

### Sorting still not working?

1. **Check filter_backends order**: `JqGridOrderingFilter` should be in the list
2. **Verify ordering_fields**: Field must be in `ordering_fields` to be sortable
3. **Check field names**: Ensure jqGrid column names match model field names
4. **Related fields**: Use double underscore notation (e.g., `category__name`)

### Debug tips:

```python
# Add logging to see what parameters are received
def list(self, request, *args, **kwargs):
    print(f"Sort params: sidx={request.GET.get('sidx')}, sord={request.GET.get('sord')}")
    return super().list(request, *args, **kwargs)
```

## Benefits

1. **Zero client-side changes**: Works with existing jqGrid configurations
2. **Backward compatible**: Standard DRF `ordering` parameter still works
3. **Full feature support**: Multi-column sorting, related fields, etc.
4. **Secure**: Validates against `ordering_fields` to prevent information disclosure