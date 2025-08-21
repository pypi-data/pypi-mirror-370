# Django Flexi Tag - Complete Usage Guide

## Service-Only Architecture 🚀

Django Flexi Tag uses a ## Advanced Patterns

### Conditional Tag Operations

```python
def apply_business_rules(order):
    service = TaggableService()

    # Auto-tag based on business logic
    if order.total_amount > 10000:
        service.add_tag(order, 'high_value')

    if order.customer.is_vip:
        service.add_tag(order, 'vip_customer')

    if order.created_date == timezone.now().date():
        service.add_tag(order, 'today')

    # Remove expired tags
    if 'flash_sale' in service.get_tags(order):
        if not order.is_flash_sale_active():
            service.remove_tag(order, 'flash_sale')
```

### Batch Processing

```python
def process_monthly_orders():
    """Process all orders from last month with batch operations"""
    last_month = timezone.now() - timedelta(days=30)
    orders = Order.objects.filter(created_date__gte=last_month)

    # Batch tag all orders from last month
    service = TaggableService()
    service.bulk_add_tags_with_many_instances(orders, ['processed', 'archived'])

    # Remove temporary tags
    temp_tagged = service.filter_by_tag(orders, 'temporary')
    service.bulk_remove_tags_with_many_instances(temp_tagged, ['temporary'])
```

### Custom Tag Validation

```python
class ValidatedTaggableService(TaggableService):
    """Extended service with custom validation"""

    ALLOWED_TAGS = {
        'Order': ['urgent', 'priority', 'vip', 'archived', 'processed'],
        'Product': ['featured', 'sale', 'new', 'discontinued'],
    }

    def add_tag(self, instance, key):
        model_name = instance.__class__.__name__
        if key not in self.ALLOWED_TAGS.get(model_name, []):
            raise ValueError(f"Tag '{key}' not allowed for {model_name}")

        return super().add_tag(instance, key)

    def bulk_add_tags(self, instance, keys):
        model_name = instance.__class__.__name__
        allowed = self.ALLOWED_TAGS.get(model_name, [])
        invalid_tags = [key for key in keys if key not in allowed]

        if invalid_tags:
            raise ValueError(f"Invalid tags for {model_name}: {invalid_tags}")

        return super().bulk_add_tags(instance, keys)

# Usage
validated_service = ValidatedTaggableService()
validated_service.add_tag(order, 'urgent')  # OK
validated_service.add_tag(order, 'invalid')  # Raises ValueError
```

### Tag Analytics

```python
def get_tag_analytics(model_class, date_range=None):
    """Get analytics for tag usage"""
    from django.db.models import Count
    from collections import Counter

    queryset = model_class.objects.all()
    if date_range:
        queryset = queryset.filter(created_date__range=date_range)

    # Get all instances with tags
    service = TaggableService()
    tagged_queryset = service.with_tags(queryset)

    # Collect all tags
    all_tags = []
    tag_model_name = f"{model_class.__name__}Tag"

    for instance in tagged_queryset:
        tag_instance = getattr(instance, tag_model_name.lower(), None)
        if tag_instance and tag_instance.tags:
            all_tags.extend(tag_instance.tags)

    # Return analytics
    return {
        'total_tagged_items': tagged_queryset.count(),
        'total_tags': len(all_tags),
        'unique_tags': len(set(all_tags)),
        'tag_frequency': Counter(all_tags),
        'most_common_tags': Counter(all_tags).most_common(10),
    }

# Usage
analytics = get_tag_analytics(Order, date_range=['2024-01-01', '2024-01-31'])
print(f"Most common tags: {analytics['most_common_tags']}")
```

## Migration Guide

### From Previous Versions

If you were using an older approach:

```python
# ✅ Current way (service-based)
service = TaggableService()
service.filter_by_tag(Order.objects.all(), 'urgent')
service.exclude_by_tag(Order.objects.all(), 'archived')
service.with_tags(Order.objects.all())

# ✅ Even better - compose with existing QuerySets
orders = Order.objects.filter(status='active').select_related('customer')
urgent_orders = service.filter_by_tag(orders, 'urgent')
```

### Updating Your Code

1. **Use service calls for tag operations:**
```python
# Current approach
service = TaggableService()
queryset = service.filter_by_tag(MyModel.objects.all(), 'important')
```

2. **Leverage QuerySet composition:**
```python
# Powerful composition
service = TaggableService()
complex_queryset = (MyModel.objects
                    .filter(status='active')
                    .select_related('user')
                    .prefetch_related('items'))
urgent_complex = service.filter_by_tag(complex_queryset, 'urgent')
```

3. **Update ViewSets:**
```python
# Current approach
class MyViewSet(TaggableViewSetMixin, viewsets.ModelViewSet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.taggable_service = TaggableService()

    def get_queryset(self):
        queryset = MyModel.objects.filter(is_enabled=True)
        return self.taggable_service.filter_by_tag(queryset, 'active')
```

## Performance Tips

### 1. Use `with_tags()` for Efficient Loading

```python
# ❌ Causes N+1 queries
orders = Order.objects.filter(status='active')
for order in orders:
    tags = service.get_tags(order)  # Database hit for each order!

# ✅ Efficient loading
service = TaggableService()
orders = service.with_tags(Order.objects.filter(status='active'))
for order in orders:
    tags = order.ordertag.tags  # No additional database hits!
```

### 2. Combine Multiple Filters

```python
# ❌ Multiple database queries
service = TaggableService()
urgent = service.filter_by_tag(Order.objects.all(), 'urgent')
priority = service.filter_by_tag(urgent, 'priority')

# ✅ Single optimized query
both_tags = service.filter_by_tags(Order.objects.all(), ['urgent', 'priority'])
```

### 3. Use Appropriate Indexing

Make sure your PostgreSQL database has GIN indexes on the tags JSONField:

```python
# This is automatically created by the generated tag models
class OrderTag(models.Model):
    instance = models.OneToOneField(Order, on_delete=models.CASCADE, primary_key=True)
    tags = JSONField(default=list)

    class Meta:
        indexes = [
            GinIndex(fields=['tags']),  # Efficient for containment queries
        ]
```

## Troubleshooting

### Common Issues

1. **Tag model not found error:**
   ```bash
   # Run the generation command
   python manage.py generate_tag_models
   python manage.py makemigrations
   python manage.py migrate
   ```

2. **QuerySet has no model attribute:**
   ```python
   # Make sure you're passing a QuerySet, not a list
   queryset = Order.objects.filter(status='active')  # ✅ QuerySet
   result = TaggableService.filter_by_tag(queryset, 'urgent')

   # Not this
   items = list(Order.objects.all())  # ❌ List
   ```

3. **Tags not appearing:**
   ```python
   # Make sure tag model is properly imported in models.py
   from .flexi_generated_model import OrderTag  # noqa
   ```

## Best Practices

1. **Always compose with existing QuerySets**
2. **Use `with_tags()` when you need to access tag data**
3. **Validate tags in your business logic layer**
4. **Use bulk operations for large datasets**
5. **Keep tag names consistent and meaningful**
6. **Consider tag lifecycle in your business processes**

This service-only architecture gives you maximum flexibility while keeping your code clean, performant, and maintainable! 🚀

## Table of Contents

1. [Model Definition](#model-definition)
2. [Tag Model Generation](#tag-model-generation)
3. [Instance Operations](#instance-operations)
4. [QuerySet Filtering](#queryset-filtering)
5. [API Integration](#api-integration)
6. [ViewSet Integration](#viewset-integration)
7. [Advanced Patterns](#advanced-patterns)
8. [Migration Guide](#migration-guide)

## Model Definition

### Basic Usage

```python
from django.db import models
from flexi_tag.utils.models import FlexiTagMixin

class Order(FlexiTagMixin):
    name = models.CharField(max_length=100)
    status = models.CharField(max_length=50)
    created_date = models.DateField()

    class Meta:
        app_label = 'myapp'
```

### With Custom QuerySets (Fully Supported!)

```python
class CustomManager(models.Manager):
    def active(self):
        return self.filter(status='active')

    def recent(self):
        return self.filter(created_date__gte=timezone.now() - timedelta(days=7))

class Product(FlexiTagMixin):
    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now_add=True)

    objects = CustomManager()  # Works seamlessly!

    class Meta:
        app_label = 'myapp'
```

### Multiple Inheritance

```python
class TimestampMixin(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class Article(TimestampMixin, FlexiTagMixin):
    title = models.CharField(max_length=200)
    content = models.TextField()

    class Meta:
        app_label = 'blog'
```

## Tag Model Generation

### Basic Command

```bash
# Generate tag models for all FlexiTagMixin models
python manage.py generate_tag_models

# See what would be generated without creating files
python manage.py generate_tag_models --dry-run

# Force reload apps to detect new models
python manage.py generate_tag_models --force-reload
```

### Generated Files

The command creates:

1. **`flexi_generated_model.py`** in your app directory:
```python
from django.db import models
from flexi_tag.utils.compat import JSONField

class OrderTag(models.Model):
    instance = models.OneToOneField(
        "myapp.Order",
        on_delete=models.CASCADE,
        primary_key=True,
    )
    tags = JSONField(default=list)

    class Meta:
        app_label = "myapp"

class ProductTag(models.Model):
    instance = models.OneToOneField(
        "myapp.Product",
        on_delete=models.CASCADE,
        primary_key=True,
    )
    tags = JSONField(default=list)

    class Meta:
        app_label = "myapp"
```

2. **Import statement** added to your `models.py`:
```python
from .flexi_generated_model import OrderTag, ProductTag  # noqa
```

3. **Migration files** automatically created via `makemigrations`

### Apply Migrations

```bash
python manage.py migrate
```

## Instance Operations

```python
from flexi_tag.utils.service import TaggableService

# Create a service instance for instance operations
service = TaggableService()

# Create some instances
order = Order.objects.create(name="Order #123", status="active")
product = Product.objects.create(name="Widget Pro", is_active=True)
```

### Adding Tags

```python
# Add single tag
service.add_tag(order, "urgent")
service.add_tag(order, "priority")

# Bulk add tags
service.bulk_add_tags(order, ["important", "customer_vip"])

# Add tags to multiple instances
orders = Order.objects.filter(status="pending")
service.bulk_add_tags_with_many_instances(orders, ["needs_review", "batch_001"])
```

### Removing Tags

```python
# Remove single tag
service.remove_tag(order, "urgent")

# Bulk remove tags
service.bulk_remove_tags(order, ["important", "customer_vip"])

# Remove tags from multiple instances
orders = Order.objects.filter(status="completed")
service.bulk_remove_tags_with_many_instances(orders, ["needs_review"])
```

### Getting Tags

```python
# Get all tags for an instance
tags = service.get_tags(order)  # Returns: ["priority", "important", "customer_vip"]

# Handle cases where no tags exist
tags = service.get_tags(new_order)  # Returns: []
```

## QuerySet Filtering

**This is the power of the service-only approach!** You can compose QuerySets with your existing filters and add tag filtering seamlessly.

### Basic Filtering

```python
## API Integration

### Custom List Views

```python
from rest_framework.generics import ListAPIView
from flexi_tag.utils.service import TaggableService
from .models import Order
from .serializers import OrderSerializer

class OrderListAPIView(ListAPIView):
    serializer_class = OrderSerializer

    def get_queryset(self):
        queryset = Order.objects.all()

        # Apply regular filters
        status = self.request.query_params.get('status')
        if status:
            queryset = queryset.filter(status=status)

        created_date = self.request.query_params.get('created_date')
        if created_date:
            queryset = queryset.filter(created_date=created_date)

        customer_id = self.request.query_params.get('customer')
        if customer_id:
            queryset = queryset.filter(customer_id=customer_id)

        # Apply tag filtering - preserves all previous filters!
        tag = self.request.query_params.get('tag')
        if tag:
            queryset = TaggableService.filter_by_tag(queryset, tag)

        # Multiple tags (AND logic)
        tags = self.request.query_params.getlist('tags')
        if tags:
            queryset = TaggableService.filter_by_tags(queryset, tags)

        # Exclude archived
        if self.request.query_params.get('exclude_archived'):
            queryset = TaggableService.exclude_by_tag(queryset, 'archived')

        return queryset

# Usage Examples:
# /api/v1/orders/?status=active&tag=urgent
# /api/v1/orders/?created_date=2024-01-01&tag=priority
# /api/v1/orders/?customer=123&tags=urgent&tags=vip
# /api/v1/orders/?exclude_archived=true&tag=pending
```

### Advanced Filtering Views

```python
class AdvancedOrderFilterView(ListAPIView):
    serializer_class = OrderSerializer

    def get_queryset(self):
        queryset = Order.objects.select_related('customer').prefetch_related('items')

        # Apply complex business logic
        if self.request.user.is_staff:
            queryset = queryset.all()
        else:
            queryset = queryset.filter(customer=self.request.user.customer_profile)

        # Date range filtering
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        if start_date and end_date:
            queryset = queryset.filter(created_date__range=[start_date, end_date])

        # Tag-based filtering with business logic
        priority_filter = self.request.query_params.get('priority')
        if priority_filter == 'high':
            queryset = TaggableService.filter_by_any_tag(queryset, ['urgent', 'priority', 'vip'])
        elif priority_filter == 'normal':
            queryset = TaggableService.exclude_by_tag(queryset, 'urgent')
            queryset = TaggableService.exclude_by_tag(queryset, 'priority')

        # Performance optimization
        queryset = TaggableService.with_tags(queryset)

        return queryset
```

## ViewSet Integration

### Basic ViewSet with TaggableViewSetMixin

```python
from rest_framework import viewsets
from flexi_tag.utils.views import TaggableViewSetMixin
from .models import Order
from .serializers import OrderSerializer

class OrderViewSet(TaggableViewSetMixin, viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def get_queryset(self):
        queryset = super().get_queryset()

        # Add custom filtering while preserving tag functionality
        if not self.request.user.is_staff:
            queryset = queryset.filter(customer=self.request.user.customer_profile)

        return queryset

# This automatically provides these endpoints:
# POST /api/orders/1/add_tag/ - {"key": "urgent"}
# POST /api/orders/1/bulk_add_tag/ - {"keys": ["urgent", "priority"]}
# POST /api/orders/1/remove_tag/ - {"key": "urgent"}
# POST /api/orders/1/bulk_remove_tags/ - {"keys": ["urgent", "priority"]}
# GET  /api/orders/1/get_tags/
# GET  /api/orders/filter_by_tag/?key=urgent
# GET  /api/orders/exclude_by_tag/?key=archived
```

### Custom ViewSet Actions

```python
class ProductViewSet(TaggableViewSetMixin, viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    @action(detail=False, methods=['get'])
    def featured(self, request):
        """Get all featured products"""
        queryset = TaggableService.filter_by_tag(
            self.get_queryset().filter(is_active=True),
            'featured'
        )

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def by_category_and_tags(self, request):
        """Advanced filtering by category and tags"""
        category = request.query_params.get('category')
        tags = request.query_params.getlist('tags')

        queryset = self.get_queryset()

        if category:
            queryset = queryset.filter(category=category)

        if tags:
            queryset = TaggableService.filter_by_tags(queryset, tags)

        # Exclude discontinued products
        queryset = TaggableService.exclude_by_tag(queryset, 'discontinued')

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

# Usage:
# GET /api/products/featured/
# GET /api/products/by_category_and_tags/?category=electronics&tags=sale&tags=popular
```
```

### Advanced Filtering

```python
# Multiple tags (AND logic) - all tags must be present
multi_tagged = TaggableService.filter_by_tags(orders, ['urgent', 'priority'])

# Any tag (OR logic) - any of the tags can be present
any_tagged = TaggableService.filter_by_any_tag(orders, ['urgent', 'priority', 'vip'])

# Complex QuerySet composition
result = (Order.objects
          .select_related('customer')
          .prefetch_related('items')
          .filter(status='active')
          .filter(created_date__gte=timezone.now() - timedelta(days=30)))

# Add tag filtering while preserving all the above
urgent_recent_orders = TaggableService.filter_by_tag(result, 'urgent')
```

### Working with Custom QuerySets

```python
# Your custom QuerySets work seamlessly
active_products = Product.objects.active()  # Your custom method
recent_products = Product.objects.recent()  # Another custom method

# Combine with tag filtering
featured_active = TaggableService.filter_by_tag(active_products, 'featured')
urgent_recent = TaggableService.filter_by_tag(recent_products, 'urgent')

# Chain multiple filters
result = (Product.objects
          .active()
          .recent())
tagged_result = TaggableService.filter_by_tag(result, 'special')
final_result = TaggableService.exclude_by_tag(tagged_result, 'discontinued')
```

### Performance Optimization

```python
# Use with_tags for efficient tag loading
queryset = Order.objects.filter(status='active')
optimized_queryset = TaggableService.with_tags(queryset)

# Now iterating won't cause N+1 queries
for order in optimized_queryset:
    print(f"Order {order.name} tags: {order.ordertag.tags}")
```

### API View Usage

```python
from rest_framework.generics import ListAPIView
from flexi_tag.utils.service import TaggableService
from .models import Order
from .serializers import OrderSerializer

class OrderListAPIView(ListAPIView):
    serializer_class = OrderSerializer

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
            queryset = TaggableService.filter_by_tag(queryset, tag)

        return queryset

# Usage: /api/v1/orders/?status=active&created_date=2024-01-01&tag=urgent
```

### ViewSet Mixin (Ready to Use)

```python
from flexi_tag.utils.views import TaggableViewSetMixin
from rest_framework.viewsets import ModelViewSet

class OrderViewSet(TaggableViewSetMixin, ModelViewSet):
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

## Why Service-Only is Better

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
# Chain multiple operations
result = (Order.objects
          .filter(status='active')
          .pipe(lambda qs: TaggableService.filter_by_tag(qs, 'urgent'))
          .filter(created_date__gte=today))
```

### ✅ **Explicit and Clear**
```python
# It's always clear what you're doing
TaggableService.filter_by_tag(queryset, 'tag')  # Obvious service call
```

## Migration from Previous Versions

If you were using older approaches:

```python
# Current service approach (recommended)
TaggableService.filter_by_tag(Order.objects.all(), 'urgent')

# Even better - compose with your existing queryset
my_orders = Order.objects.filter(status='active')
urgent_orders = TaggableService.filter_by_tag(my_orders, 'urgent')
```
