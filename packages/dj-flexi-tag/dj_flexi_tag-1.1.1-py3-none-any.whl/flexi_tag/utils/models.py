from django.db import models

from flexi_tag.utils.model_managers import TaggableManager


class FlexiTagMixin(models.Model):
    """
    Mixin for tag model generation.
    This mixin doesn't add any fields to the model itself.
    It's used by the generate_tag_models command to identify models that should have
    a corresponding tag model generated.

    The tag model will be generated as:

    class YourModelTag(models.Model):
        instance = models.OneToOneField(
            "app_label.YourModel",
            on_delete=models.CASCADE,
            primary_key=True,
        )
        tags = JSONField(default=dict)  # Uses the appropriate JSONField for your Django version

        class Meta:
            indexes = [GinIndex(fields=["tags"])]

    Usage:
        from flexi_tag.utils.models import FlexiTagMixin

        class YourModel(FlexiTagMixin):
            # your model fields here
            pass

    After defining your models, run:
        python manage.py generate_tag_models

    This will create flexi_generated_model.py files in the same directories as your models.

    To use the tags functionality, use the FlexiTagService:
        from flexi_tag.utils.service import FlexiTagService

        # Add a tag
        FlexiTagService.add_tag(instance, 'key')

        # Get all tags
        tags_dict = FlexiTagService.get_tags(instance)

        # Remove a tag
        FlexiTagService.remove_tag(instance, 'key')
    """

    tag_objects = TaggableManager()

    class Meta:
        abstract = True
