# Django Flexi Tag

[![Build status](https://img.shields.io/bitbucket/pipelines/akinonteam/dj-flexi-tag)](https://bitbucket.org/akinonteam/dj-flexi-tag/addon/pipelines/home)
[![Documentation status](https://readthedocs.org/projects/dj-flexi-tag/badge/?version=latest)](https://dj-flexi-tag.readthedocs.io/en/latest/?badge=latest)
![PyPI](https://img.shields.io/pypi/v/dj-flexi-tag)
![PyPI - Django version](https://img.shields.io/pypi/djversions/dj-flexi-tag)
![PyPI - Python version](https://img.shields.io/pypi/pyversions/dj-flexi-tag)
![PyPI - License](https://img.shields.io/badge/License-MIT-green.svg)

A flexible and efficient tagging system for Django models that allows you to add, remove, and manage tags on any Django model with minimal configuration. Built with a **service-only architecture** for maximum compatibility and composability.

## Features

- **🚀 Service-Only Architecture**: Clean and composable design with full QuerySet compatibility
- **🔄 Composable Filtering**: Preserves existing QuerySet filters when adding tag filtering
- **⚡ Easy Integration**: Works seamlessly with Django REST Framework ViewSets
- **📦 Flexible Tag Storage**: Uses PostgreSQL JSONField for efficient and flexible tag storage
- **🤖 Automatic Model Generation**: Generates auxiliary Tag models for your existing models
- **📊 Bulk Operations**: Support for bulk tag operations on multiple objects
- **🔧 Custom Exception Support**: Configure your own base exception class for seamless integration
- **🌐 Django Compatibility**: Works across multiple Django versions (1.11 to 5.0)
- **🐍 Python Compatibility**: Supports Python 3.5+

## Installation

Installation using pip:

```bash
pip install dj-flexi-tag
```

For development and testing:

```bash
pip install dj-flexi-tag[dev,test]
```

For documentation development:

```bash
pip install dj-flexi-tag[docs]
```

For all dependencies:

```bash
pip install dj-flexi-tag[dev,test,docs]
```

Add `flexi_tag` to your `INSTALLED_APPS`:

```python
INSTALLED_APPS = (
    # other apps here...
    'flexi_tag',
)
```

## Testing

Run the tests with:

```
python runtests.py
```

Use the `--verbose` flag for more detailed output:

```
python runtests.py --verbose
```

Use the `--interactive` flag for interactive mode:

```
python runtests.py --interactive
```

## Quick Start

### 1. Define Your Models with FlexiTagMixin

```python
from django.db import models
from flexi_tag.utils.models import FlexiTagMixin

class Order(FlexiTagMixin):
    name = models.CharField(max_length=100)
    status = models.CharField(max_length=50)
    created_date = models.DateField()

    class Meta:
        app_label = 'myapp'

# Your custom QuerySet methods work perfectly!
class CustomManager(models.Manager):
    def active(self):
        return self.filter(status='active')

class Product(FlexiTagMixin):
    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)

    objects = CustomManager()  # Your custom logic is preserved!

    class Meta:
        app_label = 'myapp'
```

### 2. Generate Tag Models

Run the management command:

```bash
# Standard usage
python manage.py generate_tag_models

# For testing what would be generated
python manage.py generate_tag_models --dry-run

# If models aren't detected after recent changes (force reload)
python manage.py generate_tag_models --force-reload
```

This will create a `flexi_generated_model.py` file in the same directory as your model, containing `OrderTag` and `ProductTag` models. The command will automatically:

- Generate the tag models with JSONField for tags
- Add import statements to your models.py file
- Run `makemigrations` to create migration files

### 3. Apply Migrations

```bash
python manage.py migrate
```

## Service-Only Usage 🚀

### Instance Operations

```python
from flexi_tag.utils.service import TaggableService

# Create a service instance for instance operations
service = TaggableService()

# Add tags to an instance
order = Order.objects.create(name="Order #123", status="active")
service.add_tag(order, "urgent")
service.add_tag(order, "priority")

# Bulk add tags
service.bulk_add_tags(order, ["important", "customer_vip"])

# Remove tags
service.remove_tag(order, "urgent")

# Get all tags for an instance
tags = service.get_tags(order)  # Returns: ["priority", "important", "customer_vip"]
```

### QuerySet Filtering (The Power of Service-Only!)

```python
# This is where the service-only approach shines!
# You can compose querysets with your existing filters + tag filters

# Create a service instance for filtering operations
service = TaggableService()

# Start with your existing queryset
orders = Order.objects.filter(status='active').filter(created_date__gte='2024-01-01')

# Add tag filtering - preserves all existing filters!
urgent_orders = service.filter_by_tag(orders, 'urgent')

# Chain multiple tag filters
priority_urgent = service.filter_by_tag(urgent_orders, 'priority')

# Or exclude by tag
non_archived = service.exclude_by_tag(orders, 'archived')

# Multiple tags (AND logic)
multi_tagged = service.filter_by_tags(orders, ['urgent', 'priority'])

# Any tag (OR logic)
any_tagged = service.filter_by_any_tag(orders, ['urgent', 'priority', 'vip'])

# Prefetch tag data for performance
orders_with_tags = service.with_tags(orders)
```

### API Integration

```python
from rest_framework.generics import ListAPIView
from flexi_tag.utils.service import TaggableService
from .models import Order
from .serializers import OrderSerializer

class OrderListAPIView(ListAPIView):
    serializer_class = OrderSerializer

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.taggable_service = TaggableService()

    def get_queryset(self):
        queryset = Order.objects.all()

        # Apply regular filters
        status = self.request.query_params.get('status')
        if status:
            queryset = queryset.filter(status=status)

        created_date = self.request.query_params.get('created_date')
        if created_date:
            queryset = queryset.filter(created_date=created_date)

        # Apply tag filter - preserves all previous filters!
        tag = self.request.query_params.get('tag')
        if tag:
            queryset = self.taggable_service.filter_by_tag(queryset, tag)

        return queryset

# Usage: /api/v1/orders/?status=active&created_date=2024-01-01&tag=urgent
```

### ViewSet Integration

```python
from rest_framework import viewsets
from flexi_tag.utils.views import TaggableViewSetMixin
from .models import Order

class OrderViewSet(TaggableViewSetMixin, viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

# This gives you endpoints like:
# POST /api/orders/1/add_tag/ - {"key": "urgent"}
# POST /api/orders/1/bulk_add_tag/ - {"keys": ["urgent", "priority"]}
# POST /api/orders/1/remove_tag/ - {"key": "urgent"}
# GET  /api/orders/1/get_tags/
# GET  /api/orders/filter_by_tag/?key=urgent
# GET  /api/orders/exclude_by_tag/?key=archived
```

## Why Service-Only Architecture? 🤔

### ✅ **Preserves Existing QuerySets**
```python
# Your complex querysets work perfectly
orders = Order.objects.select_related('customer').prefetch_related('items')
filtered = TaggableService.filter_by_tag(orders, 'urgent')  # All relations preserved!
```

### ✅ **Clean Integration**
```python
# Your custom QuerySets integrate seamlessly
products = Product.objects.active()  # Your custom method
tagged = TaggableService.filter_by_tag(products, 'featured')  # Service layer
```

### ✅ **Composable and Chainable**
```python
# Chain multiple operations seamlessly
result = (Order.objects
          .filter(status='active')
          .pipe(lambda qs: TaggableService.filter_by_tag(qs, 'urgent'))
          .filter(created_date__gte=today))
```

### ✅ **Explicit and Clear**
```python
# It's always clear what you're doing
TaggableService.filter_by_tag(queryset, 'tag')  # Obvious service call
# Clean, explicit, and maintainable
```

## Testing

Run the tests with:

```bash
python runtests.py
```

Use the `--verbose` flag for more detailed output:

```bash
python runtests.py --verbose
```

Use the `--interactive` flag for interactive mode:

```bash
python runtests.py --interactive
```

## Custom Exception Integration

Configure your own base exception class for seamless integration with your project:

```python
# settings.py
FLEXI_TAG_BASE_EXCEPTION_CLASS = 'myproject.exceptions.BaseAPIException'

# Now all Flexi Tag exceptions inherit from your base class
from flexi_tag.exceptions import TagValidationException

try:
    service.add_tag(instance, 'duplicate_tag')
except TagValidationException as e:
    # Has your custom base class attributes!
    print(e.status_code)  # From your BaseAPIException
```

For detailed examples and integration patterns, see [CUSTOM_EXCEPTIONS.md](CUSTOM_EXCEPTIONS.md).

## Documentation

For comprehensive documentation including advanced usage, custom validation, and detailed API reference, please visit: [https://dj-flexi-tag.readthedocs.io](https://dj-flexi-tag.readthedocs.io)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

### Development Setup

1. Clone the repository
2. Create a virtual environment
3. Install dependencies: `pip install -e .[dev,test,docs]`
4. Run tests: `python runtests.py`

## License

This project is licensed under the MIT License.
