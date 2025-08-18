# Django jqGrid Architecture

## System Architecture Overview

```mermaid
graph TB
    subgraph "Frontend Layer"
        Browser[Web Browser]
        JQGrid[jqGrid Library]
        JSCore[jqgrid-core.js]
        JSInt[jqgrid-integration.js]
        JSConf[jqgrid-config.js]
        JSCSRF[jqgrid-csrf.js]
        Templates[Django Templates]
    end
    
    subgraph "Django Backend"
        subgraph "ViewSet Layer"
            ViewSet[Custom ViewSet]
            ConfigMixin[JqGridConfigMixin]
            BulkMixin[JqGridBulkActionMixin]
        end
        
        subgraph "Data Processing"
            Serializers[DRF Serializers]
            Pagination[OptimizedPaginator]
            Filters[GridFilter Model]
            Utils[Utility Functions]
        end
        
        subgraph "REST API"
            ConfigAPI[/jqgrid_config/]
            DataAPI[/list/]
            BulkAPI[/bulk_action/]
            FilterAPI[/grid-filters/]
        end
    end
    
    subgraph "Database"
        Models[Django Models]
        GridFilterDB[(GridFilter Storage)]
    end
    
    Browser --> JQGrid
    JQGrid --> JSCore
    JSCore --> JSInt
    JSInt --> JSConf
    JSInt --> JSCSRF
    Templates --> Browser
    
    JSInt --> ConfigAPI
    JSInt --> DataAPI
    JSInt --> BulkAPI
    JSInt --> FilterAPI
    
    ViewSet --> ConfigMixin
    ViewSet --> BulkMixin
    
    ConfigAPI --> ConfigMixin
    DataAPI --> ViewSet
    BulkAPI --> BulkMixin
    FilterAPI --> Filters
    
    ViewSet --> Serializers
    ViewSet --> Pagination
    ConfigMixin --> Utils
    
    Serializers --> Models
    Filters --> GridFilterDB
    ViewSet --> Models
```

## Component Architecture

```mermaid
graph LR
    subgraph "Python Package Structure"
        django_jqgrid[django_jqgrid/]
        
        django_jqgrid --> mixins[mixins.py<br/>- JqGridConfigMixin<br/>- JqGridBulkActionMixin]
        django_jqgrid --> views[views.py<br/>- GridFilterViewSet]
        django_jqgrid --> models[models.py<br/>- GridFilter]
        django_jqgrid --> serializers[serializers.py<br/>- GridFilterSerializer]
        django_jqgrid --> pagination[pagination.py<br/>- OptimizedPaginator]
        django_jqgrid --> utils[utils.py<br/>- Helper functions]
        django_jqgrid --> filters[filters.py<br/>- Custom filters]
        django_jqgrid --> ordering[ordering.py<br/>- Ordering utilities]
        
        django_jqgrid --> static[static/]
        static --> css[CSS files]
        static --> js[JavaScript files]
        static --> plugins[jqGrid plugins]
        
        django_jqgrid --> templates[templates/]
        django_jqgrid --> templatetags[templatetags/]
    end
```

## Data Flow Architecture

```mermaid
sequenceDiagram
    participant User
    participant Browser
    participant jqGrid
    participant Django
    participant Database
    
    User->>Browser: Load page
    Browser->>Django: Request HTML
    Django->>Browser: Return template with grid
    
    Browser->>jqGrid: Initialize grid
    jqGrid->>Django: GET /api/model/jqgrid_config/
    Django->>Django: Generate config from model
    Django->>jqGrid: Return grid configuration
    
    jqGrid->>Django: GET /api/model/?page=1&rows=25
    Django->>Database: Query with pagination
    Database->>Django: Return data
    Django->>Django: Serialize data
    Django->>jqGrid: Return JSON response
    jqGrid->>Browser: Render grid
    
    User->>jqGrid: Apply filter
    jqGrid->>Django: GET /api/model/?filters={...}
    Django->>Database: Query with filters
    Database->>Django: Filtered data
    Django->>jqGrid: Return filtered results
    
    User->>jqGrid: Bulk update
    jqGrid->>Django: POST /api/model/bulk_action/
    Django->>Database: Update multiple records
    Database->>Django: Success
    Django->>jqGrid: Return status
    jqGrid->>Browser: Update display
```

## Class Hierarchy

```mermaid
classDiagram
    class ViewSet {
        +get_queryset()
        +list()
        +create()
        +update()
        +destroy()
    }
    
    class JqGridConfigMixin {
        +visible_columns
        +search_fields
        +ordering_fields
        +jqgrid_field_overrides
        +get_jqgrid_config()
        +initialize_columns()
        +get_field_config()
    }
    
    class JqGridBulkActionMixin {
        +bulk_updateable_fields
        +bulk_action()
        +validate_bulk_action()
        +perform_bulk_update()
        +perform_bulk_delete()
    }
    
    class GridFilter {
        +user
        +name
        +model_name
        +filters
        +column_widths
        +is_default
    }
    
    class OptimizedPaginator {
        +page_size
        +max_page_size
        +paginate_queryset()
        +get_paginated_response()
    }
    
    ViewSet <|-- JqGridConfigMixin
    ViewSet <|-- JqGridBulkActionMixin
    JqGridConfigMixin --> GridFilter
    JqGridBulkActionMixin --> OptimizedPaginator
```

## Frontend Architecture

```mermaid
graph TD
    subgraph "JavaScript Module Structure"
        Config[jqgrid-config.js<br/>Default Settings]
        Core[jqgrid-core.js<br/>Core Functions]
        Integration[jqgrid-integration.js<br/>Django Integration]
        CSRF[jqgrid-csrf.js<br/>CSRF Protection]
        Theme[jqgrid-theme-switcher.js<br/>Theme Management]
        
        Config --> Core
        Core --> Integration
        CSRF --> Integration
        Theme --> Core
    end
    
    subgraph "jqGrid Lifecycle"
        Init[Initialize Grid]
        LoadConfig[Load Configuration]
        FetchData[Fetch Data]
        Render[Render Grid]
        Events[Handle Events]
        
        Init --> LoadConfig
        LoadConfig --> FetchData
        FetchData --> Render
        Render --> Events
        Events --> FetchData
    end
```

## API Architecture

```mermaid
graph LR
    subgraph "REST API Endpoints"
        ListAPI[GET /api/model/<br/>List with pagination]
        DetailAPI[GET /api/model/id/<br/>Single record]
        CreateAPI[POST /api/model/<br/>Create record]
        UpdateAPI[PUT /api/model/id/<br/>Update record]
        DeleteAPI[DELETE /api/model/id/<br/>Delete record]
        ConfigAPI[GET /api/model/jqgrid_config/<br/>Grid configuration]
        BulkAPI[POST /api/model/bulk_action/<br/>Bulk operations]
        FilterAPI[GET /api/grid_filters/<br/>User filters]
    end
    
    subgraph "Request Flow"
        Request[HTTP Request]
        URLRouter[URL Router]
        ViewSet[ViewSet]
        Serializer[Serializer]
        Response[JSON Response]
        
        Request --> URLRouter
        URLRouter --> ViewSet
        ViewSet --> Serializer
        Serializer --> Response
    end
```

## Configuration Flow

```mermaid
graph TD
    Model[Django Model] --> MetaData[Model Metadata]
    MetaData --> ConfigMixin[JqGridConfigMixin]
    
    ConfigMixin --> FieldInspection[Field Inspection]
    ConfigMixin --> CustomOverrides[Custom Overrides]
    ConfigMixin --> Permissions[Permission Check]
    
    FieldInspection --> ColModel[Column Model]
    CustomOverrides --> ColModel
    Permissions --> ColModel
    
    ColModel --> GridConfig[Grid Configuration]
    GridConfig --> JSON[JSON Response]
    JSON --> jqGrid[jqGrid Initialization]
```

## Template Tag Architecture

```mermaid
graph TD
    Template[Django Template]
    
    Template --> LoadTags[load jqgrid_tags]
    
    LoadTags --> CSSTag[jqgrid_css tag]
    LoadTags --> JSTag[jqgrid_js tag]
    LoadTags --> DepsTag[jqgrid_dependencies tag]
    LoadTags --> ThemeTag[jqgrid_theme tag]
    
    CSSTag --> RenderCSS[Render CSS Links]
    JSTag --> RenderJS[Render JS Scripts]
    DepsTag --> RenderDeps[Render jQuery/Bootstrap]
    ThemeTag --> RenderTheme[Apply Theme]
```

## Security Architecture

```mermaid
graph TB
    subgraph "Security Layers"
        CSRF[CSRF Protection]
        Auth[Authentication]
        Perms[Permissions]
        Valid[Input Validation]
        
        CSRF --> Request[Request Processing]
        Auth --> Request
        Perms --> Request
        Request --> Valid
        Valid --> Process[Business Logic]
    end
    
    subgraph "Permission Checks"
        ViewPerm[View Permission]
        AddPerm[Add Permission]
        ChangePerm[Change Permission]
        DeletePerm[Delete Permission]
        BulkPerm[Bulk Action Permission]
    end
```

## Deployment Architecture

```mermaid
graph TD
    subgraph "Production Setup"
        WebServer[Web Server<br/>Nginx/Apache]
        Django[Django App]
        Static[Static Files]
        Media[Media Files]
        Database[(Database)]
        Cache[(Cache<br/>Redis/Memcached)]
        
        WebServer --> Django
        WebServer --> Static
        WebServer --> Media
        Django --> Database
        Django --> Cache
    end
    
    subgraph "Development Setup"
        DevServer[Django Dev Server]
        DevDB[(SQLite)]
        
        DevServer --> DevDB
    end
```

## Plugin Extension Points

```mermaid
graph LR
    subgraph "Extension Hooks"
        Formatters[Custom Formatters]
        Validators[Custom Validators]
        Actions[Custom Actions]
        Buttons[Custom Buttons]
        Events[Event Handlers]
    end
    
    subgraph "Override Points"
        ConfigOverride[get_jqgrid_config method]
        FieldOverride[jqgrid_field_overrides]
        BulkOverride[validate_bulk_action method]
        SerializerOverride[get_serializer_class method]
    end
```

## Performance Optimization Points

```mermaid
graph TD
    subgraph "Backend Optimizations"
        SelectRelated[select_related method]
        PrefetchRelated[prefetch_related method]
        OnlyFields[only and defer methods]
        DBIndex[Database Indexes]
        QueryOptimize[Query Optimization]
    end
    
    subgraph "Frontend Optimizations"
        LazyLoad[Lazy Loading]
        VirtualScroll[Virtual Scrolling]
        ClientCache[Client-side Caching]
        Minification[JS/CSS Minification]
    end
    
    subgraph "Caching Strategy"
        ConfigCache[Configuration Cache]
        DataCache[Data Cache]
        StaticCache[Static File Cache]
    end
```

## Error Handling Flow

```mermaid
graph TD
    Request[Request] --> TryBlock{Try}
    TryBlock --> Success[Process Request]
    TryBlock --> Error[Exception]
    
    Error --> ValidationError[Validation Error]
    Error --> PermissionError[Permission Denied]
    Error --> NotFound[404 Not Found]
    Error --> ServerError[500 Server Error]
    
    ValidationError --> Response400[400 Bad Request]
    PermissionError --> Response403[403 Forbidden]
    NotFound --> Response404[404 Not Found]
    ServerError --> Response500[500 Internal Error]
    
    Success --> Response200[200 OK]
```

## Key Design Patterns

### 1. Mixin Pattern
- `JqGridConfigMixin`: Adds grid configuration capability
- `JqGridBulkActionMixin`: Adds bulk operations
- Allows flexible composition of features

### 2. Strategy Pattern
- Different formatters for different field types
- Pluggable pagination strategies
- Customizable filtering backends

### 3. Template Method Pattern
- Base configuration methods that can be overridden
- Hook methods for customization
- Standard flow with extension points

### 4. Factory Pattern
- Automatic configuration generation from models
- Dynamic column model creation
- Serializer field mapping

### 5. Observer Pattern
- JavaScript event handlers
- Grid state change notifications
- Real-time update capabilities

## Integration Points

1. **Django REST Framework**
   - ViewSets and Mixins
   - Serializers
   - Pagination
   - Filtering

2. **Django ORM**
   - Model introspection
   - Query optimization
   - Database operations

3. **jqGrid Library**
   - Grid initialization
   - Event handling
   - Data formatting
   - UI interactions

4. **Bootstrap/jQuery UI**
   - Theme integration
   - Responsive design
   - UI components

## Data Flow Summary

1. **Configuration Phase**
   - Model metadata extraction
   - Permission checking
   - Column model generation
   - Grid options setup

2. **Data Loading Phase**
   - Request parsing
   - Query building
   - Database fetching
   - Serialization
   - Pagination

3. **Interaction Phase**
   - Event handling
   - CRUD operations
   - Bulk actions
   - Filter management

4. **Response Phase**
   - Data formatting
   - Error handling
   - Status codes
   - JSON response