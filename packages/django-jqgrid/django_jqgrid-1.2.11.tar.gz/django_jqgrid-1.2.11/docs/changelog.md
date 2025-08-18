# Changelog

All notable changes to django-jqgrid will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.2.2] - 2025-01-05

### Added
- Advanced conditional formatting support for grid cells
- Row grouping with aggregation functions (sum, count, avg)
- Frozen columns feature for better horizontal scrolling
- Custom grid filters per user functionality
- Bulk update capabilities for multiple fields
- Enhanced dropdown data caching for foreign keys

### Changed
- Improved serializer field type detection
- Enhanced permission checking for bulk operations
- Optimized JavaScript bundle size
- Updated Bootstrap 5 compatibility

### Fixed
- Fixed date filtering issues with timezone-aware dates
- Resolved memory leak in grid refresh operations
- Fixed bulk delete confirmation dialog
- Corrected currency formatter decimal places

## [1.2.1] - 2025-01-04

### Added
- Support for Django 4.2 and 5.0
- New field formatters: currency, percentage, file size
- Custom action buttons configuration
- Excel export with formatting preservation
- Grid state persistence (column widths, positions)

### Changed
- Migrated from jQuery UI to Bootstrap modals
- Improved responsive behavior on mobile devices
- Enhanced error messaging for CRUD operations

### Fixed
- Fixed compatibility with Django REST Framework 3.15
- Resolved issues with multi-select filters
- Fixed pagination reset on filter changes

## [1.2.0] - 2025-01-03

### Added
- Comprehensive template tag system for easy grid integration
- Multi-database support with database routing
- Advanced search dialog with saved searches
- Column reordering via drag and drop
- Print-friendly grid view
- CSV import with field mapping UI

### Changed
- Redesigned configuration API for better extensibility
- Improved performance for large datasets (10k+ rows)
- Enhanced documentation with more examples

### Security
- Added rate limiting for bulk operations
- Improved input sanitization for search queries
- Enhanced CSRF token validation

## [1.1.0] - 2025-01-02

### Added
- Bootstrap 5 theme support
- Real-time grid updates via WebSocket (optional)
- Advanced filtering with date ranges
- Column-specific search operators
- Export templates for custom formats
- Inline editing with validation

### Changed
- Refactored JavaScript modules for better maintainability
- Improved error handling in CRUD operations
- Updated all dependencies to latest stable versions

### Fixed
- Fixed memory issues with large exports
- Resolved timezone handling in date filters
- Fixed edge case in permission checking

## [1.0.2] - 2025-01-01

### Added
- Dark mode support for all themes
- Keyboard navigation shortcuts
- Grid toolbar customization options
- Support for computed/annotated fields

### Changed
- Improved initial load performance
- Better handling of null/empty values
- Enhanced mobile touch support

### Fixed
- Fixed issue with boolean field filtering
- Resolved CSS conflicts with admin interface
- Corrected decimal field formatting

## [1.0.1] - 2025-01-01

### Added
- Comprehensive utility functions module for common operations
- Content type caching to reduce database queries
- Optimized paginator to avoid unnecessary count queries
- Utility functions for jqGrid filter parsing and response building
- Model field information helper functions
- Export value formatting utilities

### Changed
- Optimized GridFilterViewSet queryset with select_related
- Added caching for ContentType lookups in views
- Improved get_tmplgilters method to use cached content types
- Enhanced pagination with OptimizedPaginator class

### Performance
- Reduced database queries through strategic caching
- Added select_related to optimize related field lookups
- Implemented content type caching with 1-hour timeout
- Optimized queryset evaluation in bulk operations

## [1.0.0] - 2024-01-15

### Added
- Initial release of django-jqgrid
- Auto-configuration system for Django models
- Full CRUD support with REST API integration
- Advanced filtering and search capabilities
- Import/Export functionality for Excel and CSV
- Bulk actions support
- Field-level permissions
- Query optimization with automatic select_related/prefetch_related
- Configuration caching for improved performance
- Comprehensive template tag system
- Management command for model discovery
- Multi-database support
- Responsive grid layouts
- Custom formatter support
- JavaScript hooks for extensibility
- Extensive configuration options via Django settings
- Field-specific configuration methods
- Permission-based field visibility
- Dynamic model loading
- Custom bulk action handlers
- Theme support (Bootstrap 4/5, jQuery UI)
- Internationalization support

### Security
- CSRF protection enabled by default
- Field-level permission checks
- XSS prevention in formatters