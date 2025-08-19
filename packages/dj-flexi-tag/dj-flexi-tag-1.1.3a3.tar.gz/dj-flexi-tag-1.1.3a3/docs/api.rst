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
        Mixin for tag model generation.
        This mixin doesn't add any fields to the model itself.
        It's used by the generate_tag_models command to identify models that should have
        a corresponding tag model generated.
        """

        objects = TaggableManager()

        class Meta:
            abstract = True

TaggableService
-------------

.. code-block:: python

    class TaggableService:
        """
        Service class for managing tags on model instances.
        """

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

.. code-block:: python

    class TagNotFoundException(Exception):
        """
        Raised when a tag is not found.
        """

    class TagNotDefinedException(Exception):
        """
        Raised when a tag key is not provided.
        """

    class TagValidationException(Exception):
        """
        Raised when tag validation fails.
        """

    class ObjectIDsNotDefinedException(Exception):
        """
        Raised when object IDs are not provided for bulk operations.
        """

Compatibility
===========

The library includes compatibility functions to work with different Django versions:

.. code-block:: python

    # JSONField location changed in Django 3.1
    if django.VERSION >= (3, 1):
        from django.db.models import JSONField
    else:
        from django.contrib.postgres.fields import JSONField
        Parse a string of tags into a list of cleaned tag names.
        """

    def get_tag_cloud(queryset_or_model, min_count=None, steps=4):
        """
        Generate a tag cloud for the given queryset or model.

        Returns tags with a 'font_size' attribute (1-steps) based on frequency.
        """

    def related_objects_by_tags(obj, model_class, min_tags=1):
        """
        Find objects of the given model class that share tags with obj.

        Returns a queryset ordered by number of shared tags.
        """
