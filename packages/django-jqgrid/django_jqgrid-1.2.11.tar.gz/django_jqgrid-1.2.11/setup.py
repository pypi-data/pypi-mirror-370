#!/usr/bin/env python
import os
from setuptools import setup, find_packages

# Read the README file
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read version from __init__.py
def get_version():
    init_file = os.path.join(os.path.dirname(__file__), 'django_jqgrid', '__init__.py')
    with open(init_file, 'r') as f:
        for line in f:
            if line.startswith('__version__'):
                return line.split('=')[1].strip().strip('"').strip("'")
    return '0.1.0'

setup(
    name='django-jqgrid',
    version=get_version(),
    author='Your Name',
    author_email='your.email@example.com',
    description='A Django app for integrating jqGrid with Django REST Framework',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/coder-aniket/django-jqgrid',
    packages=find_packages(exclude=[
        'tests*', 
        'docs*', 
        'example_project*',
        'example_env*',
        '.venv*',
        'venv*',
        'env*',
        'ENV*',
        '.env*',
        'virtualenv*',
        'build*',
        'dist*',
        '.eggs*',
        '*.egg-info',
        '.claude*',
        '.vscode*',
        '.idea*',
    ]),
    include_package_data=True,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 3.2',
        'Framework :: Django :: 4.0',
        'Framework :: Django :: 4.1',
        'Framework :: Django :: 4.2',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    python_requires='>=3.8',
    install_requires=[
        'Django>=3.2',
        'djangorestframework>=3.12.0',
        'django-filter>=21.1',
    ],
    extras_require={
        'dev': [
            'pytest>=6.2',
            'pytest-django>=4.4',
            'pytest-cov>=2.12',
            'black>=21.7b0',
            'flake8>=3.9',
            'isort>=5.9',
            'mypy>=0.910',
            'django-stubs>=1.9',
            'djangorestframework-stubs>=1.4',
        ],
        'production': [
            'redis>=3.5.0',  # For caching
            'celery>=5.1.0',  # For background tasks
        ],
        'import-export': [
            'openpyxl>=3.0.0',  # Excel import/export
            'xlsxwriter>=3.0.0',  # Excel export with formatting
            'reportlab>=3.6.0',  # PDF export
            'Pillow>=8.0.0',  # Image handling
        ],
        'docs': [
            'sphinx>=5.0.0',
            'sphinx-rtd-theme>=1.0.0',
            'myst-parser>=0.18.0',
            'linkify-it-py>=1.0',
            'django>=3.2.0',
            'djangorestframework>=3.12.0',
        ],
    },
    keywords='django jqgrid rest framework grid datatable',
    project_urls={
        'Bug Reports': 'https://github.com/coder-aniket/django-jqgrid/issues',
        'Source': 'https://github.com/coder-aniket/django-jqgrid',
        'Documentation': 'https://django-jqgrid.readthedocs.io',
    },
)