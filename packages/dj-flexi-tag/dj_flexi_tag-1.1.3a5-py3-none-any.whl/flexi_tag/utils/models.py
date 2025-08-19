from django.db import models


class FlexiTagMixin(models.Model):
    """
    Mixin for tag model generation.

    This mixin is used by the generate_tag_models command to identify models
    that should have a corresponding tag model generated.

    The mixin doesn't add any fields to the model itself. It serves as a marker
    to indicate that a model should have tag functionality.

    The tag model will be generated as:

    class YourModelTag(models.Model):
        instance = models.OneToOneField(
            "app_label.YourModel",
            on_delete=models.CASCADE,
            primary_key=True,
        )
        tags = JSONField(default=list)  # Uses the appropriate JSONField for your Django version

        class Meta:
            indexes = [GinIndex(fields=["tags"])]

    Usage Examples:

    1. Basic usage:
        class YourModel(FlexiTagMixin):
            name = models.CharField(max_length=100)

    After defining your models, run:
        python manage.py generate_tag_models

    This will create flexi_generated_model.py files in the same directories as your models.

    To use the tags functionality, use the TaggableService:
        from flexi_tag.utils.service import TaggableService

        # Add a tag
        TaggableService().add_tag(instance, 'key')

        # Filter by tag (preserves existing queryset filters!)
        queryset = YourModel.objects.filter(is_active=True)
        tagged_items = TaggableService.filter_by_tag(queryset, 'important')

        # Get all tags
        tags_list = TaggableService().get_tags(instance)

        # Remove a tag
        TaggableService().remove_tag(instance, 'key')
    """

    class Meta:
        abstract = True
