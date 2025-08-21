"""
Django Flexi Tag - Flexible tagging system for Django with service-only architecture.

This package provides a flexible tagging system for Django models using a clean
service-only architecture that avoids manager conflicts and provides powerful
QuerySet composition capabilities.

Key Components:
- FlexiTagMixin: Simple abstract model marker for taggable models
- TaggableService: Core service with both instance and static methods
- TaggableViewSetMixin: DRF ViewSet integration for REST APIs

Example Usage:
    from flexi_tag.utils.models import FlexiTagMixin
    from flexi_tag.utils.service import TaggableService

    class Article(FlexiTagMixin):
        title = models.CharField(max_length=200)

    # Add tags to instances
    service = TaggableService()
    service.add_tag(article, 'featured')

    # Filter QuerySets by tags
    featured = service.filter_by_tag(Article.objects.all(), 'featured')
"""

__version__ = "2.0.0"  # Major version bump for service-only architecture
__author__ = "Akinon"
__license__ = "MIT"

default_app_config = "flexi_tag.apps.FlexiTagConfig"

# Note: Components are not imported here to avoid Django setup issues.
# Import them directly from their modules:
#   from flexi_tag.utils.models import FlexiTagMixin
#   from flexi_tag.utils.service import TaggableService
#   from flexi_tag.utils.views import TaggableViewSetMixin

__all__ = [
    "__version__",
]
