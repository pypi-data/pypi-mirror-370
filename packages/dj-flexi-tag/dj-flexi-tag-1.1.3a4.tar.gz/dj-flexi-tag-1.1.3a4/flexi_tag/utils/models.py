from django.db import models

from flexi_tag.utils.model_managers import TaggableManager


class FlexiTagMeta(type(models.Model)):
    """
    Metaclass that ensures models always have both 'objects' and 'tag_objects' managers.

    This metaclass intelligently detects if a user has defined a custom 'objects' manager
    and preserves it while ensuring 'tag_objects' is always available for tag operations.
    """

    def __new__(cls, name, bases, namespace, **kwargs):
        # Create the new class
        new_class = super(FlexiTagMeta, cls).__new__(
            cls, name, bases, namespace, **kwargs
        )

        # Skip for abstract models and the mixin itself
        if getattr(new_class._meta, "abstract", False) or name == "FlexiTagMixin":
            return new_class

        # Check if user has defined a custom objects manager
        has_custom_objects = False

        # Check if 'objects' is defined directly in this class
        if "objects" in namespace:
            has_custom_objects = True
        else:
            # Check through the method resolution order for custom objects managers
            for base in bases:
                if hasattr(base, "objects"):
                    objects_manager = getattr(base, "objects")
                    # Check if it's not the default Django Manager
                    if (
                        not isinstance(objects_manager, models.Manager)
                        or type(objects_manager) is not models.Manager
                    ):
                        has_custom_objects = True
                        break

        # If no custom objects manager exists, add the default one
        if not has_custom_objects and not hasattr(new_class, "objects"):
            new_class.add_to_class("objects", models.Manager())

        # Always ensure tag_objects exists (but don't override if user defined it)
        if not hasattr(new_class, "tag_objects"):
            new_class.add_to_class("tag_objects", TaggableManager())

        return new_class


class FlexiTagMixin(models.Model, metaclass=FlexiTagMeta):
    """
    Mixin for tag model generation.

    This mixin automatically ensures that models have both 'objects' and 'tag_objects' managers,
    while preserving any custom 'objects' manager defined by the user.

    The mixin doesn't add any fields to the model itself. It's used by the generate_tag_models
    command to identify models that should have a corresponding tag model generated.

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

    Usage Examples:

    1. Basic usage (gets default 'objects' + 'tag_objects'):
        class YourModel(FlexiTagMixin):
            name = models.CharField(max_length=100)

        # Both managers are available:
        YourModel.objects.all()              # Standard Django manager
        YourModel.tag_objects.filter_tag()   # Tag-specific operations

    2. With custom manager (preserves your custom 'objects'):
        class CustomManager(models.Manager):
            def active(self):
                return self.filter(is_active=True)

        class YourModel(FlexiTagMixin):
            name = models.CharField(max_length=100)
            is_active = models.BooleanField(default=True)
            objects = CustomManager()  # This is preserved!

        # Both managers work:
        YourModel.objects.active()           # Your custom manager method
        YourModel.tag_objects.filter_tag()   # Tag operations

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

    class Meta:
        abstract = True
