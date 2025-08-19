# Migration Guide: Manager-Based to Service-Only Architecture

## Overview

Django Flexi Tag has migrated from a manager-based architecture to a **service-only architecture** for better compatibility, composability, and maintainability.

## What Changed?

### ❌ **Removed (No Longer Available)**

- `TaggableManager` class
- `tag_objects` manager on models
- Manager-based filtering methods:
  - `Model.tag_objects.filter_tag()`
  - `Model.tag_objects.exclude_tag()`
  - `Model.tag_objects.with_tags()`

### ✅ **Added (New Service-Only Approach)**

- Enhanced `TaggableService` with static filtering methods
- Simplified `FlexiTagMixin` (just a marker, no metaclass)
- Full QuerySet composition support
- Zero manager conflicts

## Migration Steps

### Step 1: Update Your Code

**Before (Manager-Based):**
```python
# ❌ This no longer works
urgent_orders = Order.tag_objects.filter_tag('urgent')
active_products = Product.tag_objects.exclude_tag('discontinued')
orders_with_tags = Order.tag_objects.with_tags()
```

**After (Service-Only):**
```python
# ✅ New approach
urgent_orders = TaggableService.filter_by_tag(Order.objects.all(), 'urgent')
active_products = TaggableService.exclude_by_tag(Product.objects.all(), 'discontinued')
orders_with_tags = TaggableService.with_tags(Order.objects.all())
```

### Step 2: Leverage QuerySet Composition

**Before (Limited):**
```python
# Could only start fresh from tag_objects manager
urgent_orders = Order.tag_objects.filter_tag('urgent')
```

**After (Powerful):**
```python
# Can compose with any existing QuerySet!
complex_queryset = (Order.objects
                    .filter(status='active')
                    .select_related('customer')
                    .prefetch_related('items')
                    .filter(created_date__gte=last_week))

urgent_complex = TaggableService.filter_by_tag(complex_queryset, 'urgent')
```

### Step 3: Update ViewSets

**Before:**
```python
class OrderViewSet(TaggableViewSetMixin, viewsets.ModelViewSet):
    def get_queryset(self):
        if some_condition:
            return Order.tag_objects.filter_tag('special')
        return Order.objects.all()
```

**After:**
```python
class OrderViewSet(TaggableViewSetMixin, viewsets.ModelViewSet):
    def get_queryset(self):
        queryset = Order.objects.all()
        if some_condition:
            queryset = TaggableService.filter_by_tag(queryset, 'special')
        return queryset
```

### Step 4: Update Custom Manager Integration

**Before (Problematic):**
```python
class Order(FlexiTagMixin):
    objects = CustomManager()  # Could conflict with tag_objects
```

**After (Perfect):**
```python
class Order(FlexiTagMixin):
    objects = CustomManager()  # No conflicts, works perfectly!

# Usage:
active_orders = Order.objects.active()  # Your custom method
urgent_active = TaggableService.filter_by_tag(active_orders, 'urgent')
```

## Benefits of Migration

### 1. **No More Manager Conflicts**
```python
# Your custom managers always work
products = Product.objects.active().featured()
tagged = TaggableService.filter_by_tag(products, 'on_sale')
```

### 2. **QuerySet Composition**
```python
# Build complex queries step by step
base = Order.objects.select_related('customer')
filtered = base.filter(status='active')
recent = filtered.filter(created_date__gte=last_week)
tagged = TaggableService.filter_by_tag(recent, 'priority')
```

### 3. **Explicit and Clear**
```python
# Always obvious what's happening
TaggableService.filter_by_tag(queryset, 'tag')  # Clear service call
```

### 4. **Enhanced Functionality**
```python
# New methods not available before
multi_tags = TaggableService.filter_by_tags(queryset, ['urgent', 'priority'])
any_tags = TaggableService.filter_by_any_tag(queryset, ['urgent', 'priority'])
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

### Error: "AttributeError: 'Model' object has no attribute 'tag_objects'"

**Cause:** You're still using the old manager-based syntax.

**Solution:** Replace with service calls:
```python
# Change this:
Model.tag_objects.filter_tag('tag')

# To this:
TaggableService.filter_by_tag(Model.objects.all(), 'tag')
```

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
base = Order.objects.all()
filtered1 = TaggableService.filter_by_tag(base, 'tag1')
filtered2 = TaggableService.filter_by_tag(filtered1, 'tag2')

# Use combined filtering:
combined = TaggableService.filter_by_tags(Order.objects.all(), ['tag1', 'tag2'])
```

## Testing Your Migration

1. **Run existing tests** - They should pass with the new service approach
2. **Test QuerySet composition** - Verify filtering works with your existing queries
3. **Check custom managers** - Ensure your custom manager methods still work
4. **Validate performance** - New approach should be same or better performance

## Summary

The migration to service-only architecture provides:

- ✅ **Better compatibility** with existing Django patterns
- ✅ **More powerful QuerySet composition**
- ✅ **Cleaner, more explicit code**
- ✅ **Zero manager conflicts**
- ✅ **Enhanced functionality** with new filtering methods

The new approach is more flexible, more powerful, and more maintainable than the previous manager-based system!
