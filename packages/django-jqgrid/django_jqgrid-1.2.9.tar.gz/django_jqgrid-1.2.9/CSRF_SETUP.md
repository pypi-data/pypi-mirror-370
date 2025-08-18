# CSRF Token Setup in django-jqgrid

The django-jqgrid package now automatically handles CSRF tokens for all AJAX requests using jQuery's `$.ajaxSetup()` configuration.

## How it Works

1. **Automatic Setup**: When you include `{% jqgrid_js %}` in your template, it automatically loads `jqgrid-csrf.js` which configures CSRF handling.

2. **Token Sources**: The CSRF token is obtained from (in order of preference):
   - Cookie (`csrftoken`)
   - Meta tag (`<meta name="csrf-token">`)
   - Hidden input field (`{% csrf_token %}`)

3. **Smart Handling**: CSRF tokens are only sent for:
   - Same-origin requests
   - Non-safe HTTP methods (POST, PUT, DELETE, PATCH)

## Usage

Simply ensure you have a CSRF token in your template:

```django
{% load jqgrid_tags %}

<!-- Include jqGrid JS (includes CSRF setup) -->
{% jqgrid_js %}

<!-- Include CSRF token -->
{% csrf_token %}
```

## Migration from window.token

If you were previously using `window.token` for CSRF handling, you can remove all such references. The new setup handles this automatically:

**Before:**
```javascript
$.ajax({
    url: '/api/endpoint/',
    method: 'POST',
    headers: window.token || {},
    // ...
});
```

**After:**
```javascript
$.ajax({
    url: '/api/endpoint/',
    method: 'POST',
    // CSRF token is automatically included
    // ...
});
```

## Custom AJAX Requests

All jQuery AJAX requests will automatically include the CSRF token. No additional configuration is needed for:
- jqGrid CRUD operations
- Filter saving/deleting
- Bulk operations
- Import/export
- Custom AJAX calls

## Troubleshooting

If you encounter CSRF token issues:

1. Ensure `{% csrf_token %}` is in your template
2. Check that `django.middleware.csrf.CsrfViewMiddleware` is in `MIDDLEWARE`
3. For API views, ensure proper authentication is configured
4. Check browser console for CSRF-related errors

## Benefits

- **Cleaner Code**: No need to manually add CSRF tokens to each AJAX request
- **Consistent**: All AJAX requests are handled uniformly
- **Secure**: Follows Django's CSRF protection best practices
- **Automatic**: Works with all jqGrid operations out of the box