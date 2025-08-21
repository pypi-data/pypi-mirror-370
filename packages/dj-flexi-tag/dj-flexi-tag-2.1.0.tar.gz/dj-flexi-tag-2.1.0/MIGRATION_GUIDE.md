# Migration Guide: Upgrading to Service-Only Architecture

## Overview

Django Flexi Tag has evolved to use a **service-only architecture** for better compatibility, composability, and maintainability. This guide helps you understand the current approach and migrate from any previous patterns.

## What's Available Now?

### ✅ **Current Service-Only Approach**

- Enhanced `TaggableService` with instance and static filtering methods
- Simplified `FlexiTagMixin` (just a marker, clean and simple)
- Full QuerySet composition support
- Clean integration with existing Django patterns

## Migration Steps

### Step 1: Use the Service-Only Approach

**Current Service-Only Pattern:**
```python
# ✅ Service-based approach
service = TaggableService()
urgent_orders = service.filter_by_tag(Order.objects.all(), 'urgent')
active_products = service.exclude_by_tag(Product.objects.all(), 'discontinued')
orders_with_tags = service.with_tags(Order.objects.all())
```

### Step 2: Leverage QuerySet Composition

**Powerful Composition:**
```python
# Can compose with any existing QuerySet!
service = TaggableService()
complex_queryset = (Order.objects
                    .filter(status='active')
                    .select_related('customer')
                    .prefetch_related('items')
                    .filter(created_date__gte=last_week))

urgent_complex = service.filter_by_tag(complex_queryset, 'urgent')
```

### Step 3: Update ViewSets

**Current Pattern:**
```python
class OrderViewSet(TaggableViewSetMixin, viewsets.ModelViewSet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.taggable_service = TaggableService()

    def get_queryset(self):
        queryset = Order.objects.all()
        if some_condition:
            queryset = self.taggable_service.filter_by_tag(queryset, 'special')
        return queryset
```

### Step 4: Clean Integration with Custom QuerySets

**Seamless Integration:**
```python
class Order(FlexiTagMixin):
    objects = CustomManager()  # Your custom logic works seamlessly!

# Usage:
service = TaggableService()
active_orders = Order.objects.active()  # Your custom method
urgent_active = service.filter_by_tag(active_orders, 'urgent')
```

## Benefits of Service-Only Architecture

### 1. **Clean Integration**
```python
# Your custom QuerySets always work
service = TaggableService()
products = Product.objects.active().featured()
tagged = service.filter_by_tag(products, 'on_sale')
```

### 2. **QuerySet Composition**
```python
# Build complex queries step by step
service = TaggableService()
base = Order.objects.select_related('customer')
filtered = base.filter(status='active')
recent = filtered.filter(created_date__gte=last_week)
tagged = service.filter_by_tag(recent, 'priority')
```

### 3. **Explicit and Clear**
```python
# Always obvious what's happening
service = TaggableService()
service.filter_by_tag(queryset, 'tag')  # Clear service call
```

### 4. **Enhanced Functionality**
```python
# New methods not available before
service = TaggableService()
multi_tags = service.filter_by_tags(queryset, ['urgent', 'priority'])
any_tags = service.filter_by_any_tag(queryset, ['urgent', 'priority'])
```

## API Compatibility

### ViewSet Mixin (Unchanged)

The `TaggableViewSetMixin` API remains exactly the same:

```python
# These endpoints still work the same:
POST /orders/1/add_tag/ - {"key": "urgent"}
POST /orders/1/bulk_add_tag/ - {"keys": ["urgent", "priority"]}
GET  /orders/filter_by_tag/?key=urgent
```

### Service Instance Methods (Unchanged)

```python
# These methods work exactly the same:
service = TaggableService()
service.add_tag(instance, 'key')
service.bulk_add_tags(instance, ['key1', 'key2'])
service.remove_tag(instance, 'key')
service.get_tags(instance)
```

## Troubleshooting

### Error: "Tag model not found"

**Cause:** Tag models haven't been generated or migrated.

**Solution:**
```bash
python manage.py generate_tag_models
python manage.py makemigrations
python manage.py migrate
```

### Performance Issues

**Cause:** Not using QuerySet composition effectively.

**Solution:** Leverage the new composition capabilities:
```python
# Instead of multiple separate queries:
service = TaggableService()
base = Order.objects.all()
filtered1 = service.filter_by_tag(base, 'tag1')
filtered2 = service.filter_by_tag(filtered1, 'tag2')

# Use combined filtering:
combined = service.filter_by_tags(Order.objects.all(), ['tag1', 'tag2'])
```

## Testing Your Migration

1. **Run existing tests** - They should pass with the new service approach
2. **Test QuerySet composition** - Verify filtering works with your existing queries
3. **Check custom managers** - Ensure your custom manager methods still work
4. **Validate performance** - New approach should be same or better performance

## Summary

The service-only architecture provides:

- ✅ **Better compatibility** with existing Django patterns
- ✅ **More powerful QuerySet composition**
- ✅ **Cleaner, more explicit code**
- ✅ **Clean integration** with any custom QuerySets
- ✅ **Enhanced functionality** with new filtering methods

The service-only approach is flexible, powerful, and maintainable!
