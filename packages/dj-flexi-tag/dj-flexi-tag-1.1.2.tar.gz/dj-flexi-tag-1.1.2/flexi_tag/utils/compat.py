"""
Compatibility module for Django version differences.
"""
import django

# JSONField location changed in Django 3.1
if django.VERSION >= (3, 1):
    from django.db.models import JSONField
else:
    from django.contrib.postgres.fields import JSONField

# GinIndex compatibility for different Django versions
try:
    from django.contrib.postgres.indexes import GinIndex
except ImportError:
    # For older Django versions that don't have GinIndex
    class GinIndex:
        def __init__(self, *args, **kwargs):
            pass
