# Custom Base Exception Configuration

Django Flexi Tag supports configurable base exception classes to integrate seamlessly with your project's exception hierarchy.

## Default Behavior

By default, Flexi Tag uses its own `DefaultProjectBaseException`:

```python
from flexi_tag.exceptions import TagValidationException, ProjectBaseException

# ProjectBaseException is DefaultProjectBaseException by default
print(ProjectBaseException.__name__)  # 'DefaultProjectBaseException'

try:
    raise TagValidationException(name="duplicate_tag")
except TagValidationException as e:
    print(e)  # "tag_100_1:Tag already exists. name: duplicate_tag"
```

## Custom Base Exception

You can configure Flexi Tag to use your project's base exception class:

### 1. Define Your Base Exception

```python
# myproject/exceptions.py
class BaseAPIException(Exception):
    """Base exception for all API errors"""
    def __init__(self, message, status_code=400, error_code=None, *args, **kwargs):
        super().__init__(message, *args, **kwargs)
        self.status_code = status_code
        self.error_code = error_code
```

### 2. Configure in Settings

```python
# settings.py
FLEXI_TAG_BASE_EXCEPTION_CLASS = 'myproject.exceptions.BaseAPIException'
```

### 3. Use Enhanced Exceptions

```python
from flexi_tag.exceptions import TagValidationException

try:
    raise TagValidationException(name="duplicate_tag")
except TagValidationException as e:
    print(e)                    # "tag_100_1:Tag already exists. name: duplicate_tag"
    print(e.status_code)        # 400 (inherited from BaseAPIException)
    print(e.error_code)         # None (inherited from BaseAPIException)
    print(type(e).__bases__)    # (<class 'myproject.exceptions.BaseAPIException'>,)
```

## Integration with Django REST Framework

Perfect for DRF projects:

```python
# settings.py
FLEXI_TAG_BASE_EXCEPTION_CLASS = 'rest_framework.exceptions.APIException'

# Now all Flexi Tag exceptions inherit from DRF's APIException
from flexi_tag.exceptions import TagValidationException
from rest_framework.exceptions import APIException

try:
    raise TagValidationException(name="invalid_tag")
except APIException as e:  # Can catch as DRF exception!
    return Response(
        {"error": str(e)},
        status=e.status_code if hasattr(e, 'status_code') else 400
    )
```

## Available Exceptions

All these exceptions support the custom base class configuration:

- `TagValidationException` - Tag already exists or validation fails
- `TagNotFoundException` - Tag not found during removal
- `TagNotDefinedException` - Required tag parameter missing
- `ObjectIDsNotDefinedException` - Required object IDs missing

## Error Codes

Each exception has a unique error code from `flexi_tag.codes`:

```python
from flexi_tag.exceptions import TagValidationException
from flexi_tag import codes

exception = TagValidationException(name="test")
print(exception.code)  # Same as codes.tag_100_1
```

## Benefits

✅ **Seamless Integration**: Fits into your existing exception hierarchy
✅ **Consistent Error Handling**: All exceptions follow your project patterns
✅ **DRF Compatible**: Works perfectly with Django REST Framework
✅ **Flexible**: Support any custom base exception class
✅ **Backward Compatible**: Default behavior unchanged if not configured

## Migration

Existing code continues to work without changes. The custom base exception is purely additive functionality!
