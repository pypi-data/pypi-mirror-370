# django-jqgrid Search and Sort Functionality Verification

## Overview

The django-jqgrid package fully implements search and sort functionality compatible with jqGrid's requirements. This document verifies the implementation details.

## ✅ Search Functionality

### 1. **Core Implementation**

#### Filter Backend (`django_jqgrid/filters.py`)
```python
class JqGridFilterBackend(BaseFilterBackend):
    """Handles jqGrid filter requests with advanced filtering"""
    
    def filter_queryset(self, request, queryset, view):
        filters = request.query_params.get('filters', None)
        search = request.query_params.get('_search', 'false')
        
        if search == 'true' and filters:
            filters_dict = json.loads(filters)
            filter_q = self.build_filter_query(filters_dict, view, queryset.model, allowed_fields)
            queryset = queryset.filter(filter_q)
```

#### Supported Search Operators
- `eq` - Equals (exact match)
- `ne` - Not equals
- `lt` - Less than
- `le` - Less than or equal
- `gt` - Greater than
- `ge` - Greater than or equal
- `cn` - Contains (case-insensitive)
- `nc` - Does not contain
- `bw` - Begins with
- `bn` - Does not begin with
- `ew` - Ends with
- `en` - Does not end with
- `in` - Is in (comma-separated values)
- `ni` - Is not in
- `nu` - Is null
- `nn` - Is not null

### 2. **ViewSet Configuration**

```python
class ProductViewSet(viewsets.ModelViewSet):
    filter_backends = [JqGridFilterBackend, DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['name', 'description', 'sku']
    allowed_filters = ['name', 'description', 'sku', 'price', 'stock_quantity', 'status']
```

### 3. **Client-Side Integration**

jqGrid sends search parameters as:
```javascript
{
    _search: 'true',
    filters: JSON.stringify({
        groupOp: 'AND',  // or 'OR'
        rules: [
            {field: 'name', op: 'cn', data: 'Product'},
            {field: 'price', op: 'gt', data: '50'}
        ]
    })
}
```

### 4. **Advanced Features**

- **Complex Grouping**: Supports nested groups with AND/OR operations
- **Type Casting**: Automatically converts string values to appropriate Python types
- **Field Validation**: Only allows searching on explicitly defined fields
- **Custom Mappings**: Supports custom filter mappings for special cases

## ✅ Sort Functionality

### 1. **Core Implementation**

#### Mixin Configuration (`django_jqgrid/mixins.py`)
```python
# In JqGridConfigMixin
ordering_fields = ['name', 'price', 'created_at']
ordering = ['-created_at']  # Default ordering

# Column configuration
col_config["sortable"] = field_name in self.ordering_fields
```

### 2. **Multi-Column Sorting**

The package supports jqGrid's multi-column sorting:
```javascript
// Client sends:
{
    sidx: 'category,price',
    sord: 'asc,desc'
}
```

Processed by:
```python
# In JqGridSortBackend
if ',' in sidx:
    field_list = sidx.split(',')
    for field_order in field_list:
        field = field_order.split(' ')[0]
        direction = field_order.split(' ')[1] if ' ' in field_order else sord
        
        if direction.lower() == 'desc':
            sort_fields.append(f"-{field}")
        else:
            sort_fields.append(field)
```

### 3. **ViewSet Configuration**

```python
class ProductViewSet(viewsets.ModelViewSet):
    filter_backends = [JqGridFilterBackend, DjangoFilterBackend, SearchFilter, OrderingFilter]
    ordering_fields = ['name', 'price', 'stock_quantity', 'created_at']
    ordering = ['-created_at']  # Default sort
```

### 4. **Column-Level Control**

Each column can be individually configured:
```python
{
    "name": "price",
    "sortable": True,  # Enable sorting
    "sorttype": "number",  # Sort as number, not string
    "firstsortorder": "desc"  # Initial sort direction
}
```

## ✅ Pagination Integration

The package includes `JqGridPagination` that works seamlessly with search and sort:

```python
class JqGridPagination(PageNumberPagination):
    page_query_param = 'page'
    page_size_query_param = 'rows'  # jqGrid uses 'rows' not 'page_size'
    
    def get_paginated_response(self, data):
        return Response({
            'page': self.page.number,
            'total': self.page.paginator.num_pages,
            'records': self.page.paginator.count,
            'rows': data  # jqGrid expects 'rows' not 'results'
        })
```

## ✅ Request/Response Flow

### Search Request Example
```
GET /api/products/?_search=true&filters={"groupOp":"AND","rules":[{"field":"name","op":"cn","data":"Pro"}]}&sidx=price&sord=desc&page=1&rows=25
```

### Response Format
```json
{
    "page": 1,
    "total": 4,
    "records": 87,
    "rows": [
        {
            "id": 1,
            "name": "Product Pro",
            "price": 99.99,
            "stock_quantity": 50
        }
    ]
}
```

## ✅ Feature Verification

### Working Features:
1. **Basic Search** ✓
   - Text search (contains, starts with, ends with)
   - Numeric comparisons (>, <, =, etc.)
   - Boolean fields
   - Date fields

2. **Advanced Search** ✓
   - Multiple conditions with AND/OR
   - Nested groups
   - Null checks
   - In/Not in lists

3. **Sorting** ✓
   - Single column sort
   - Multi-column sort
   - Ascending/descending
   - Custom sort types (number, date, text)

4. **Integration** ✓
   - Works with pagination
   - Maintains state across page changes
   - Compatible with other DRF filters
   - Respects permissions

## Testing the Functionality

### 1. Run the Example Project
```bash
cd example_project
python manage.py runserver
```

### 2. Run the Test Script
```bash
python test_search_sort.py
```

### 3. Manual Testing in Browser
1. Open http://localhost:8000/examples/
2. Go to any grid (Products, Customers, Orders)
3. Use the filter toolbar to search
4. Click column headers to sort
5. Use the search dialog (magnifying glass icon)

## Configuration Examples

### Basic Setup
```python
class MyViewSet(JqGridConfigMixin, viewsets.ModelViewSet):
    queryset = MyModel.objects.all()
    serializer_class = MySerializer
    
    # Enable search/sort
    filter_backends = [JqGridFilterBackend, OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['-created_at']
    allowed_filters = ['name', 'description', 'status']
```

### Custom Search Behavior
```python
# Override filter mappings
filter_mappings = {
    "name__jq_cn": "name__icontains",
    "code__jq_eq": "code__iexact"  # Case-insensitive exact match
}
```

### Disable Search/Sort for Specific Columns
```python
jqgrid_field_overrides = {
    'sensitive_field': {
        'search': False,
        'sortable': False
    }
}
```

## Performance Considerations

1. **Database Indexes**: Add indexes to frequently searched/sorted fields
2. **Query Optimization**: Use `select_related()` and `prefetch_related()`
3. **Limited Fields**: Only include necessary fields in `search_fields`
4. **Pagination**: Use reasonable page sizes (25-100 rows)

## Troubleshooting

### Search Not Working
1. Check `_search=true` parameter is sent
2. Verify `filters` parameter is valid JSON
3. Ensure field is in `allowed_filters` or `search_fields`
4. Check browser console for JavaScript errors

### Sort Not Working
1. Verify field is in `ordering_fields`
2. Check `sidx` and `sord` parameters
3. Ensure column has `sortable: true` in config
4. Check for database-level sort restrictions

## Conclusion

The django-jqgrid package fully implements both search and sort functionality as required by jqGrid. All standard operators are supported, complex queries work correctly, and the integration with Django REST Framework is seamless.