=============
Advanced Usage
=============

This guide covers advanced usage patterns and configurations for Django Flexi Tag.

Programmatic Tag Management
--------------------------

While the ViewSet mixins provide API endpoints for tag management, you might want to manage tags programmatically in your application code. You can do this using the TaggableService class:

.. code-block:: python

    from flexi_tag.utils.service import TaggableService

    # Create a service instance
    tag_service = TaggableService()

    # Add a single tag
    tag_service.add_tag(instance=my_object, key="important")

    # Add multiple tags
    tag_service.bulk_add_tags(instance=my_object, keys=["urgent", "follow-up"])

    # Remove a tag
    tag_service.remove_tag(instance=my_object, key="important")

    # Remove multiple tags
    tag_service.bulk_remove_tags(instance=my_object, keys=["urgent", "follow-up"])

    # Add tags to multiple objects
    queryset = MyModel.objects.filter(status="active")
    tag_service.bulk_add_tags_with_many_instances(instances=queryset, keys=["active"])

Custom Tag Model Configuration
----------------------------

The `generate_tag_models` command creates tag models with default settings, but you might want to customize this generation. You can create your own management command that extends the default one:

.. code-block:: python

    from django.core.management.base import BaseCommand
    from flexi_tag.management.commands.generate_tag_models import Command as BaseGenerateTagModelsCommand

    class Command(BaseGenerateTagModelsCommand):
        help = "Generate custom tag models for all models that inherit from FlexiTagMixin"

        def handle(self, *args, **options):
            # Customize the model template
            self.model_template = """
            # Custom model template
            from django.db import models
            from flexi_tag.utils.compat import JSONField

            class {{ model_name }}Tag(models.Model):
                instance = models.OneToOneField(
                    "{{ app_label }}.{{ model_name }}",
                    on_delete=models.CASCADE,
                    primary_key=True,
                )
                tags = JSONField(default=list)
                # Add custom fields here
                last_tagged_at = models.DateTimeField(auto_now=True)

                class Meta:
                    app_label = "{{ app_label }}"
                    db_table = "{{ app_label }}_{{ model_lower_name }}_tag"
            """
            super().handle(*args, **options)

Tag Validation
------------

You can implement custom tag validation by extending the TaggableService class:

.. code-block:: python

    from flexi_tag.utils.service import TaggableService
    from flexi_tag.exceptions import TagValidationException

    class MyTaggableService(TaggableService):
        def __validate_tag_key(self, key: str) -> bool:
            # Call the parent implementation
            super().__validate_tag_key(key)
            
            # Add custom validation
            if len(key) < 3:
                raise TagValidationException(name=key, message="Tag must be at least 3 characters long")
            
            # Only allow alphanumeric tags
            if not key.isalnum():
                raise TagValidationException(name=key, message="Tag must be alphanumeric")
                
            return True

Querying Tagged Objects
--------------------

To efficiently query objects by their tags, you can use PostgreSQL's JSON operators:

.. code-block:: python

    # Find all objects with a specific tag
    objects_with_tag = YourModel.objects.filter(yourmodeltag__tags__contains=["important"])
    
    # Find objects with any of these tags
    objects_with_any_tag = YourModel.objects.filter(yourmodeltag__tags__overlap=["urgent", "important"])

Using with Non-PostgreSQL Databases
---------------------------------

While Django Flexi Tag is optimized for PostgreSQL using its native JSON support, you can use it with other databases by customizing the tag model generation. For example, to use it with SQLite or MySQL:

1. Create a custom JSONField implementation
2. Update the model template in a custom management command
3. Ensure your database can efficiently query the tag field

Performance Considerations
-----------------------

For large datasets, consider these performance optimizations:

1. Create database indexes on the tags field
2. Use batch processing for bulk tag operations
3. Consider denormalizing critical tag data for faster queries
4. Use caching for frequently accessed tag information

Security Considerations
--------------------

When implementing tag systems, be aware of these security concerns:

1. Validate tag input to prevent injection attacks
2. Implement permission checks for tag management
3. Consider the visibility of tags in your API responses
4. Audit tag changes for sensitive data