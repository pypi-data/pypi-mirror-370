# AG Grid Django Integration Guide

This README provides a comprehensive guide on integrating AG Grid with your Django project for creating dynamic, interactive data tables with CRUD capabilities.

## Table of Contents

- Features
- Installation
- Basic Configuration
- Model Registration
- URL Configuration
- Permissions Setup
- Frontend Integration
- Advanced Configuration
  - Custom Headers
  - Filtered List Views
  - Custom Field Types
  - Custom Creation / Edition Form
  - Change Logging
  - Realtime Socket Data Transfer
  - Asynchronized Excel Export & Notification
- Troubleshooting

## Features

- 🚀 **Real-time Updates**: WebSocket-based live data synchronization
- 📊 **Advanced Filtering**: Server-side filtering with AG Grid compatibility
- 📈 **Excel Export**: Configurable Excel export with custom formatting
- 🔐 **Permission System**: Django-based permission integration
- 🔔 **Notifications**: Built-in notification system for user alerts
- 📝 **Change Logging**: Comprehensive audit trail for all operations
- 🎨 **Customizable**: Flexible configuration for headers, fields, and display options

## Installation

### 1. Install the package

```bash
pip install ag-grid-django
```

### 2. Add the app to your INSTALLED_APPS

```python
# settings.py
INSTALLED_APPS = [
    # ...
    'ag_grid',
    'ag_grid.contirb.notification', # optional, for notifications
    # ...
]
```

### 3. Install required dependencies

```bash
pip install djangorestframework
pip install drf-yasg  # For Swagger documentation
```

- openpyxl - excel export
- daphne
- channels, channels_redis - socket notification

### 4. Run migrations

```bash
python manage.py migrate
```

## Basic Configuration

### Create a configuration file

Create a file named `aggrid_admin.py` in each app where you want to use AG Grid:

```python
# yourapp/aggrid_admin.py
from ag_grid.grid import AgGrid
from ag_grid.registry import register
from yourapp.models import YourModel

@register(YourModel)
class YourModelAG(AgGrid):
    list_display = ('id', 'field1', 'field2', 'related_model__field')
    editable = ('field1', 'field2')
    sortable = ('field1', 'field2')
    left_pinning = ('id', 'field1')
    right_pinning = ('related_model__field',)

    # Optional: Configure form fields for adding/editing
    form_fields = {
        "field1": {
            "type": "text",
            "label": "Field One",
            "required": True,
            "editable": False,
            "placeholder": "Enter field one",
            "validation": {"required": "This field is required"}
        },
        "field2": {
            "type": "number",
            "label": "Field Two",
            "required": True,
            "editable": True,
            "validation": {"min": {"value": 0, "message": "Must be positive"}}
        },
        "field3": {
            "type": "select",
            "label": "Field Three",
            "required": True,
            "editable": True,
            "placeholder": "Select Field Three",
            "options": {"url": "/api/ag-grid/{app_label}/{model_name}/foreign-options/influencer/", "key": "nickname"},
            "validation": {"required": "Influencer is required"},

        }
        # Add more fields as needed
    }

    # Optional: Optimize queries
    @classmethod
    def get_queryset(cls, model):
        return model.objects.select_related('related_model')


    @classmethod
    def get_fk_display_field(cls, field_name):
        """Return the field to use for display in foreign key dropdowns"""
        if field_name == "category_fk":
            return "name"  # Use the 'name' field from Category model
        return None  # Default fallback
```

### Ensure app configuration loads your AG Grid settings for customization

```python
# yourapp/apps.py
from django.apps import AppConfig

class YourAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'yourapp'

    def ready(self):
        # Import aggrid_admin to register models
        import yourapp.aggrid_admin
```

Make sure your `__init__.py` uses this config:

```python
# yourapp/__init__.py
default_app_config = 'yourapp.apps.YourAppConfig'
```

## Model Registration

For each model you want to manage with AG Grid:

1. Import your model and the AG Grid components
2. Decorate a class with `@register(YourModel)`
3. Define display configuration:
   - `list_display`: Fields to show in the grid
   - `editable`: Fields that can be edited inline
   - `sortable`: Fields that can be sorted
   - `form_fields`: Configuration for form fields in add/edit forms
   - `header_names`: Custom header names for fields (optional)

### Example with Custom Headers

```python
@register(Product)
class ProductAG(AgGrid):
    list_display = ("id", "name", "category__name", "price", "quantity")
    editable = ("price", "quantity")
    sortable = ("name", "price", "quantity")

    # Define custom header names for fields
    header_names = {
        "id": "ID",
        "name": "Product Name",
        "price": "Sale Price",
        "quantity": "Stock Level",
        "category__name": "Category"  # Custom header for related field
    }

    form_fields = {
        "name": {
            "type": "text",
            "label": "Product Name",
            "required": True,
            "placeholder": "Enter product name",
            "validation": {"required": "Product name is required"}
        },
        # More fields...
    }
```

Custom headers are particularly useful for:

- Using more user-friendly column names in the grid
- Providing localized or translated headers
- Simplifying complex field names, especially for related fields

### Automatic Model Configuration

If a model is not registered with AG Grid, the system will automatically generate and send results based on the order of columns defined in the model. This provides a convenient fallback that allows basic functionality without explicit configuration.

## URL Configuration

### 1. Include AG Grid URLs in your project's main URLs

```python
# yourproject/urls.py
from django.urls import path, include

urlpatterns = [
    # ...
    path("api/ag-grid/", include("ag_grid.urls", namespace="ag_grid")),
    # ...
]
```

## Permissions Setup

### 1. Ensure proper model permissions exist

Make sure your models have the standard Django permissions (view, add, change, delete).

### 2. Configure your authentication system

The AG Grid views use Django REST Framework's permission system. Configure your authentication in settings.py:
Make sure you are using simplejwt to use AgGrid Package Permission

```python
# settings.py
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": ("rest_framework_simplejwt.authentication.JWTAuthentication",),
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticated",),
}

MEDIA_ROOT = os.path.join(BASE_DIR, "media")
```

### 3. Assign permissions to users

In Django Admin, assign the appropriate permissions to your users:

- `yourapp.view_yourmodel`
- `yourapp.add_yourmodel`
- `yourapp.change_yourmodel`
- `yourapp.delete_yourmodel`

## Frontend Integration

### API Endpoints

The following endpoints are available for each registered model:

- `POST /api/ag-grid/{app_label}/{model_name}/excel-export/` - Export AG Grid Data to Excel
- `GET /api/ag-grid/{app_label}/{model_name}/filtered-data-source/` - Get AG Grid Filtered List
- `GET /api/ag-grid/{app_label}/{model_name}/foreign-options/{field_name}/` - Get Foreign Key Options
- `POST /api/ag-grid/{app_label}/{model_name}/form-create/` - Create Model Instance
- `GET /api/ag-grid/{app_label}/{model_name}/form-fields/` - Get Form Field Requirements
- `GET /api/ag-grid/{app_label}/{model_name}/list-headers/` - Get AgGrid Headers
- `DELETE /api/ag-grid/{app_label}/{model_name}/{id}/delete/` - Delete Model Instance
- `PATCH /api/ag-grid/{app_label}/{model_name}/{id}/update/` - Update Model Field

### Notification Endpoints

- `GET /api/ag-grid/notifications/` - Get notifications for current users
- `POST /api/ag-grid/notifications/send-notification/` - Send a new notification
- `POST /api/ag-grid/notifications/{id}/mark-read/` - Mark notification as read

## Advanced Configuration

### Custom Headers

You can customize the display names of your grid columns by adding a `header_names` dictionary to your AgGrid class:

```python
@register(Product)
class ProductAG(AgGrid):
    list_display = ("id", "name", "price", "quantity", "category_fk")
    editable = ("price", "quantity")
    sortable = ("name", "price", "quantity")

    # Add custom header names
    header_names = {
        "id": "ID",
        "category_fk": "카테고리"  # Korean: "Category"
    }

    left_pinning = (
        "id",
        "name",
    )

    form_fields = {
        "name": {
            "type": "text",
            "label": "Product Name",
            "required": True,
            "editable": True,
            "placeholder": "Enter product name",
            "validation": {"required": "Product name is required", "minLength": {"value": 3, "message": "Name must be at least 3 characters"}},
        },
        "category": {
            "type": "raw_id",
            "label": "Category",
            "required": True,
            "editable": True,
            "placeholder": "Select a category",
            "validation": {"required": "Category is required"},
            "options": {"url": "/api/ag-grid/product/Product/foreign-options/category/", "key": "title"},
        },
        "price": {
            "type": "number",
            "label": "Price",
            "required": True,
            "editable": True,
            "placeholder": "0.00",
            "validation": {"required": "Price is required", "min": {"value": 0, "message": "Price must be positive"}},
        },
        "quantity": {
            "type": "number",
            "label": "Quantity",
            "required": True,
            "editable": True,
            "placeholder": "0",
            "validation": {"required": "Quantity is required", "min": {"value": 0, "message": "Quantity must be positive"}, "pattern": {"value": "^[0-9]+$", "message": "Must be a whole number"}},
        },
        "description": {"type": "textarea", "label": "Description", "required": False, "placeholder": "Enter product description", "rows": 4},
    }

    @classmethod
    def get_queryset(cls, model):
        return model.objects.select_related("category_fk")

    @classmethod
    def get_fk_display_field(cls, field_name):
        """Return the field to use for display in foreign key dropdowns"""
        if field_name == "category_fk":
            return "name"  # Use the 'name' field from Category model
        return None  # Default fallback
```

This allows you to:

- Display user-friendly column names
- Support internationalization by using translated terms
- Create cleaner headers for relationship fields

### Creating Filtered List Views

The `AgGridFilteredListView` class provides powerful server-side filtering, sorting, and pagination for AG Grid:

1. Create a custom view by extending `AgGridFilteredListView`:

```python
# yourapp/views.py
from ag_grid.api import AgGridFilteredListView
from django.db.models import Sum, Count, F

class ProductFilteredListView(AgGridFilteredListView):
    app_label = 'product'  # Your app label
    model_name = 'Product'  # Your model name

    def apply_custom_filters(self, queryset, request):
        # Add custom filters based on request parameters
        min_stock = request.GET.get('min_stock')
        if min_stock:
            queryset = queryset.filter(quantity__gte=min_stock)

        # Add custom annotations
        queryset = queryset.annotate(
            revenue=F('price') * F('sales_count')
        )

        return queryset
```

2. Register your custom view in URLs:

```python
# yourapp/urls.py
from django.urls import path
from .views import ProductFilteredListView

urlpatterns = [
    # ...
    path('api/filtered-products/', ProductFilteredListView.as_view(), name='filtered-products'),
]
```

3. Use with AG Grid's server-side model:

```javascript
const gridOptions = {
  rowModelType: "serverSide",
  serverSideStoreType: "partial",
  datasource: {
    getRows: function (params) {
      // Your fetch implementation to call the filtered list endpoint
    },
  },
};
```

The `AgGridFilteredListView` automatically:

- Processes AG Grid's filter models
- Applies complex filtering, including date and number ranges
- Optimizes queries with select_related based on your list_display
- Provides proper pagination and total counts
- Returns only the fields in your list_display configuration

### Custom Field Types

The system maps Django field types to AG Grid types using these mappings:

```python

FIELD_TYPE_MAP = {
    "AutoField": "number",
    "BigIntegerField": "number",
    "IntegerField": "number",
    "FloatField": "number",
    "DecimalField": "number",
    "CharField": "text",
    "TextField": "text",
    "EmailField": "text",
    "SlugField": "text",
    "BooleanField": "boolean",
    "DateField": "date",
    "DateTimeField": "datetime",
    "ForeignKey": "fk",
    "OneToOneField": "fk",
    "ManyToManyField": "m2m",
}

FILTER_TYPE_MAP = {
    "AutoField": "agNumberColumnFilter",
    "BigIntegerField": "agNumberColumnFilter",
    "IntegerField": "agNumberColumnFilter",
    "FloatField": "agNumberColumnFilter",
    "DecimalField": "agNumberColumnFilter",
    "DateField": "agDateColumnFilter",
    "DateTimeField": "agDateColumnFilter",
    "ForeignKey": "",
    "OneToOneField": "",
    "ManyToManyField": "",
}

CELL_RENDERER_MAP = {
    "BooleanField": "agCheckboxCellRenderer",
    "DateField": "agDateCellRenderer",
    "DateTimeField": "agDateCellRenderer",
    "ForeignKey": "agTextCellRenderer",
    "OneToOneField": "agTextCellRenderer",
    "ManyToManyField": "agTextCellRenderer",
}

CELL_EDITOR_MAP = {
    "BooleanField": "agCheckboxCellRenderer",
    "DateField": "agDateCellEditor",
    "ForeignKey": "agSelectCellEditor",
}
```

### Selection Configurations

You can configure selection options for fields using the `selection_configs` attribute. This is particularly useful for fields that should be displayed as radio buttons or dropdowns with predefined choices:

```python
@register(Product)
class ProductAG(AgGrid):
    list_display = ("id", "name", "status", "category", "column_name")

    selection_configs = {
        # 1. Auto-collect all available choices (all distinct values from database)
        "column_name": {
            "type": "radio" or "checkbox"
        },
    }
```

**Configuration Options:**

- **Auto-collection**: When only `type` is specified, the system automatically collects all distinct values from the database for that field
- **Custom labels**: When `labels` array is provided, these predefined options are used instead of auto-collected values
- **Types supported**: `"radio"`, `"select"`, `"checkbox"` (for multiple selections)

**Use Cases:**

- Status fields with predefined states
- Priority levels
- Category selections
- Any field where you want to limit user input to specific choices

### Change Logging

The system automatically logs all changes to a `GridEditLog` model:

- Creation of records
- Updates to field values
- Deletion of records
- Excel exports

This provides an audit trail of all changes made through the AG Grid interface.

## Troubleshooting

### Common Issues

1. **Grid config not found error**

   - Ensure your `aggrid_admin.py` file is being loaded
   - Check that you've properly registered your model

2. **Permission errors**

   - Verify the user has the appropriate permissions
   - Check authentication setup

3. **Field not editable**

   - Make sure the field is included in the `editable` tuple

4. **Related fields not showing**

   - Ensure you're using the correct field path (e.g., `category__name`)
   - Check that you've included select_related in your queryset

5. **Custom headers not appearing**
   - Verify the field names in header_names match exactly with list_display
   - Make sure get_header_names is implemented in your AgGrid class

For more help, check the documentation or open an issue in the project repository.
