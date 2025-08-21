=============
API Reference
=============

Core Components
==============

FlexiTagMixin
------------

.. code-block:: python

    class FlexiTagMixin(models.Model):
        """
        Simple abstract model mixin for tag model generation.

        This mixin doesn't add any fields to the model itself and provides
        clean integration with existing Django patterns. It's used by the
        generate_tag_models command to identify models that should have a
        corresponding tag model generated.

        Benefits of service-only approach:
        - Clean integration with existing Django patterns
        - Clear separation of concerns
        - Full QuerySet composition support
        """

        class Meta:
            abstract = True

TaggableService
-------------

The core service class that provides all tagging functionality through instance methods.

.. code-block:: python

    class TaggableService:
        """
        Service class for managing tags on model instances.

        Service-only architecture benefits:
        - Works with any QuerySet (preserves existing filters)
        - Clean integration with existing Django patterns
        - Explicit and composable operations
        - Enhanced filtering capabilities
        """

Instance Operations
~~~~~~~~~~~~~~~~~

.. code-block:: python

        def add_tag(self, instance, key: str) -> object:
            """
            Add a single tag to an instance.

            Args:
                instance: The model instance to tag
                key: The tag key (string)

            Returns:
                The tagged instance

            Raises:
                TagValidationException: If the tag already exists
            """

        def bulk_add_tags(self, instance, keys: list) -> object:
            """
            Add multiple tags to an instance.

            Args:
                instance: The model instance to tag
                keys: List of tag keys (strings)

            Returns:
                The tagged instance

            Raises:
                TagValidationException: If any tag already exists
            """

        def bulk_add_tags_with_many_instances(self, instances: QuerySet, keys: list) -> QuerySet:
            """
            Add multiple tags to multiple instances.

            Args:
                instances: QuerySet of model instances to tag
                keys: List of tag keys (strings)

            Returns:
                The QuerySet of tagged instances

            Raises:
                TagValidationException: If any tag already exists on any instance
            """

        def remove_tag(self, instance, key: str) -> object:
            """
            Remove a tag from an instance.

            Args:
                instance: The model instance to untag
                key: The tag key (string)

            Returns:
                The tag instance

            Raises:
                TagNotFoundException: If the instance is not tagged
                TagValidationException: If the tag doesn't exist on the instance
            """

        def bulk_remove_tags(self, instance, keys: list) -> object:
            """
            Remove multiple tags from an instance.

            Args:
                instance: The model instance to untag
                keys: List of tag keys (strings)

            Returns:
                The tag instance

            Raises:
                TagNotFoundException: If the instance is not tagged
            """

        def get_tags(self, instance) -> list:
            """
            Get all tags for an instance.

            Args:
                instance: The model instance

            Returns:
                List of tag keys (strings)
            """

QuerySet Operations
~~~~~~~~~~~~~~~~

The power of service-only architecture - compose with any existing QuerySet!

.. code-block:: python

        def filter_by_tag(self, queryset: QuerySet, key: str) -> QuerySet:
            """
            Filter QuerySet by tag key, preserving existing filters.

            Args:
                queryset: The QuerySet to filter
                key: The tag key to filter by

            Returns:
                Filtered QuerySet

            Example:
                # Compose with existing QuerySet filters
                active_products = Product.objects.filter(is_active=True)
                featured_active = service.filter_by_tag(active_products, 'featured')
            """

        def exclude_by_tag(self, queryset: QuerySet, key: str) -> QuerySet:
            """
            Exclude QuerySet by tag key, preserving existing filters.

            Args:
                queryset: The QuerySet to filter
                key: The tag key to exclude by

            Returns:
                Filtered QuerySet
            """

        def with_tags(self, queryset: QuerySet) -> QuerySet:
            """
            Add prefetch_related for tag objects, preserving existing QuerySet.
            Use this to avoid N+1 queries when accessing tags.

            Args:
                queryset: The QuerySet to optimize

            Returns:
                QuerySet with prefetched tag data
            """

        def filter_by_tags(self, queryset: QuerySet, tags: list) -> QuerySet:
            """
            Filter QuerySet by multiple tags (AND logic).

            Args:
                queryset: The QuerySet to filter
                tags: List of tag keys (all must be present)

            Returns:
                Filtered QuerySet
            """

        def filter_by_any_tag(self, queryset: QuerySet, tags: list) -> QuerySet:
            """
            Filter QuerySet by any of the tags (OR logic).

            Args:
                queryset: The QuerySet to filter
                tags: List of tag keys (any can be present)

            Returns:
                Filtered QuerySet
            """

TaggableViewSetMixin
-----------------

.. code-block:: python

    class TaggableViewSetMixin(object):
        """
        Mixin for Django REST Framework ViewSets that adds tag-related endpoints.
        """

        @action(detail=True, methods=["post"])
        def add_tag(self, request, pk=None):
            """
            Add a tag to an instance.

            POST /model/<pk>/add_tag/
            {"key": "tag_key"}
            """

        @action(detail=True, methods=["post"])
        def bulk_add_tag(self, request, pk=None):
            """
            Add multiple tags to an instance.

            POST /model/<pk>/bulk_add_tag/
            {"keys": ["tag1", "tag2"]}
            """

        @action(detail=False, methods=["post"])
        def bulk_add_tags(self, request, pk=None):
            """
            Add multiple tags to multiple instances.

            POST /model/bulk_add_tags/
            {"objects": [1, 2, 3], "keys": ["tag1", "tag2"]}
            """

        @action(detail=True, methods=["post"])
        def remove_tag(self, request, pk=None):
            """
            Remove a tag from an instance.

            POST /model/<pk>/remove_tag/
            {"key": "tag_key"}
            """

        @action(detail=True, methods=["post"])
        def bulk_remove_tags(self, request, pk=None):
            """
            Remove multiple tags from an instance.

            POST /model/<pk>/bulk_remove_tags/
            {"keys": ["tag1", "tag2"]}
            """

        @action(detail=False, methods=["post"])
        def bulk_remove_tags_with_many_instances(self, request, pk=None):
            """
            Remove multiple tags from multiple instances.

            POST /model/bulk_remove_tags_with_many_instances/
            {"objects": [1, 2, 3], "keys": ["tag1", "tag2"]}
            """

Management Commands
=================

generate_tag_models
-----------------

.. code-block:: python

    class Command(BaseCommand):
        """
        Management command to generate tag models for all models inheriting from FlexiTagMixin.

        Usage:
            python manage.py generate_tag_models [--dry-run]

        Options:
            --dry-run: Show what would be generated without creating files
        """

Generated Models
==============

When you run the `generate_tag_models` command, it creates a new model for each model that inherits from `FlexiTagMixin`. The generated model will look like this:

.. code-block:: python

    class YourModelTag(models.Model):
        """
        Generated tag model for YourModel.
        """
        instance = models.OneToOneField(
            "app_label.YourModel",
            on_delete=models.CASCADE,
            primary_key=True,
        )
        tags = JSONField(default=list)

        class Meta:
            app_label = "app_label"
            db_table = "app_label_yourmodel_tag"
            indexes = [GinIndex(fields=["tags"])]

        def __str__(self):
            return "Tags for {}".format(self.instance)"

Exceptions
=========

Flexi Tag provides customizable exception classes that can inherit from your project's base exception class.

Configuration
-----------

Configure your base exception class in Django settings:

.. code-block:: python

    # settings.py
    FLEXI_TAG_BASE_EXCEPTION_CLASS = 'myproject.exceptions.MyBaseException'

Available Exceptions
-----------------

.. code-block:: python

    class ProjectBaseException(Exception):
        """
        Base exception class. Can be customized via FLEXI_TAG_BASE_EXCEPTION_CLASS setting.
        Default: Uses DefaultProjectBaseException
        """

    class TagNotFoundException(ProjectBaseException):
        """
        Raised when a tag is not found.

        Default message: "Tag not found"
        """

    class TagNotDefinedException(ProjectBaseException):
        """
        Raised when a tag key is not provided.

        Default message: "Tag key not defined"
        """

    class TagValidationException(ProjectBaseException):
        """
        Raised when tag validation fails.

        Default message: "Tag validation failed"
        """

    class ObjectIDsNotDefinedException(ProjectBaseException):
        """
        Raised when object IDs are not provided for bulk operations.

        Default message: "Object IDs not defined"
        """

Usage Examples
------------

.. code-block:: python

    from flexi_tag.exceptions import TagNotFoundException, TagValidationException

    try:
        service.add_tag(instance, "nonexistent_tag")
    except TagNotFoundException as e:
        logger.error(f"Tag error: {e}")

    try:
        service.add_tag(instance, "")
    except TagValidationException as e:
        logger.error(f"Validation error: {e}")

Compatibility
===========

The library includes compatibility functions to work with different Django versions:

.. code-block:: python

    # JSONField location changed in Django 3.1
    if django.VERSION >= (3, 1):
        from django.db.models import JSONField
    else:
        from django.contrib.postgres.fields import JSONField

Utility Functions
===============

.. code-block:: python

    def parse_tag_string(tag_string, delimiter=","):
        """
        Parse a string of tags into a list of cleaned tag names.

        Args:
            tag_string: Comma-separated string of tags
            delimiter: Character to split on (default: comma)

        Returns:
            List of cleaned tag strings
        """

    def get_tag_cloud(queryset_or_model, min_count=None, steps=4):
        """
        Generate a tag cloud for the given queryset or model.

        Args:
            queryset_or_model: QuerySet or model class to analyze
            min_count: Minimum tag count to include
            steps: Number of font size steps (1-steps)

        Returns:
            Tags with a 'font_size' attribute based on frequency.
        """

    def related_objects_by_tags(obj, model_class, min_tags=1):
        """
        Find objects of the given model class that share tags with obj.

        Args:
            obj: Object with tags to match against
            model_class: Model class to search in
            min_tags: Minimum number of shared tags required

        Returns:
            QuerySet ordered by number of shared tags.
        """
