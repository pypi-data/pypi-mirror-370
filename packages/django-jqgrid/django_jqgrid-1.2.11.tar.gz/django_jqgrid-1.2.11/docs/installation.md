# Django JQGrid Installation & Setup Guide

## Quick Installation

### 1. Install the Package

```bash
pip install django-jqgrid
```

### 2. Add to Django Settings

```python
# settings.py
INSTALLED_APPS = [
    # ... your other apps
    'rest_framework',  # Required dependency
    'django_jqgrid',
]

# Django REST Framework configuration (required)
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 25
}

# Optional: Django JQGrid configuration
JQGRID_CONFIG = {
    'DEFAULT_ROWS_PER_PAGE': 25,
    'ENABLE_EXCEL_EXPORT': True,
    'ENABLE_CSV_EXPORT': True,
    'ENABLE_FILTERING': True,
    'ENABLE_CRUD_OPERATIONS': True,
}
```

### 3. Configure URLs

```python
# urls.py
from django.urls import path, include

urlpatterns = [
    # ... your other URL patterns
    path('api/', include('django_jqgrid.api_urls')),  # API endpoints
    path('jqgrid/', include('django_jqgrid.urls')),  # Optional: admin views
]
```

### 4. Run Migrations

```bash
python manage.py migrate
```

## Demo Project Setup

To see Django JQGrid in action, you can run the included demo project:

### Method 1: Automated Setup (Recommended)

```bash
# Clone the repository
git clone https://github.com/coder-aniket/django-jqgrid.git
cd django-jqgrid/example/example_project

# Run the setup script (Linux/Mac)
chmod +x setup.sh
./setup.sh

# Or run manually (Windows/Linux/Mac)
python setup_demo.py
```

### Method 2: Manual Setup

```bash
# Navigate to the demo project
cd django-jqgrid/example/example_project

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install requirements
pip install -r requirements.txt

# Setup database and sample data
python setup_demo.py

# Start the development server
python manage.py runserver
```

### Demo Access

After setup, visit: http://127.0.0.1:8000/

**Login Credentials:**
- Username: `admin`
- Password: `admin123`

**Demo Features:**
- Employee management grid
- Department management grid
- Project tracking grid
- Task management grid
- Advanced demo with all features

## Production Installation

### 1. Install with Production Dependencies

```bash
pip install django-jqgrid[production]
```

Or install optional dependencies manually:

```bash
pip install django-jqgrid
pip install openpyxl>=3.0.0      # For Excel import/export
pip install xlsxwriter>=3.0.0    # For Excel export with formatting
pip install reportlab>=3.6.0     # For PDF export
pip install Pillow>=8.0.0        # For image handling
```

### 2. Production Settings

```python
# settings.py for production
JQGRID_CONFIG = {
    'DEFAULT_ROWS_PER_PAGE': 50,
    'ENABLE_EXCEL_EXPORT': True,
    'ENABLE_CSV_EXPORT': True,
    'ENABLE_FILTERING': True,
    'ENABLE_CRUD_OPERATIONS': True,
    'MAX_EXPORT_RECORDS': 10000,
    'CACHE_TIMEOUT': 300,
    'USE_CACHE': True,
    'SECURE_EXPORTS': True,
}

# Security settings
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ],
}

# Cache configuration for better performance
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
    }
}
```

### 3. Collect Static Files

```bash
python manage.py collectstatic
```

### 4. Configure Web Server

**Nginx Configuration Example:**

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location /static/ {
        alias /path/to/your/project/staticfiles/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    location /media/ {
        alias /path/to/your/project/media/;
        expires 1y;
        add_header Cache-Control "public";
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## Troubleshooting Installation

### Common Issues

1. **Import Error: No module named 'rest_framework'**
   ```bash
   pip install djangorestframework
   ```

2. **Static files not loading**
   ```bash
   python manage.py collectstatic
   ```
   Make sure `STATIC_URL` and `STATIC_ROOT` are configured in settings.

3. **Database errors**
   ```bash
   python manage.py migrate
   ```

4. **Permission denied errors**
   ```bash
   # Make sure the setup script is executable
   chmod +x setup.sh
   ```

5. **Import/Export not working**
   - Ensure FontAwesome is loaded (check browser console)
   - Install optional dependencies:
   ```bash
   pip install openpyxl xlsxwriter reportlab
   ```

### System Requirements

**Minimum Requirements:**
- Python 3.8+
- Django 3.2+
- Django REST Framework 3.12+

**Recommended:**
- Python 3.10+
- Django 4.2+
- 512MB RAM minimum, 2GB+ recommended
- Modern web browser (Chrome, Firefox, Safari, Edge)

**Optional Dependencies:**
- Redis (for caching)
- PostgreSQL (for production databases)
- Celery (for background tasks)

### Development Environment

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run linting
flake8
black .
isort .

# Build documentation
cd docs
make html
```

### Docker Installation

```dockerfile
# Dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
```

```yaml
# docker-compose.yml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - .:/app
    environment:
      - DEBUG=1
    depends_on:
      - db
      - redis

  db:
    image: postgres:13
    environment:
      POSTGRES_DB: jqgrid_demo
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:6-alpine

volumes:
  postgres_data:
```

## Next Steps

After installation, check out:

1. [Basic Usage Guide](README.md#basic-usage)
2. [API Reference](API_REFERENCE.md)
3. [Features Documentation](FEATURES.md)
4. [Examples and Tutorials](README.md#examples)

For questions and support:
- GitHub Issues: https://github.com/coder-aniket/django-jqgrid/issues
- Documentation: https://django-jqgrid.readthedocs.io
- Email: coder.aniketp@gmail.com