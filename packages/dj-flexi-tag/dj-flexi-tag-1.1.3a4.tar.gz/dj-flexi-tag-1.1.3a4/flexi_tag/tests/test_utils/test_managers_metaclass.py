from django.db import models
from django.test import TestCase

from flexi_tag.utils.model_managers import TaggableManager
from flexi_tag.utils.models import FlexiTagMixin


class ManagerMetaclassTestCase(TestCase):
    """Test cases for the FlexiTagMeta metaclass manager resolution."""

    def test_default_manager_creation(self):
        """Test that models without custom managers get default objects manager."""
        from flexi_tag.tests.models import DefaultManagerTestModel

        # Should have both objects and tag_objects managers
        self.assertTrue(hasattr(DefaultManagerTestModel, "objects"))
        self.assertTrue(hasattr(DefaultManagerTestModel, "tag_objects"))

        # objects should be the default Django Manager
        self.assertIsInstance(DefaultManagerTestModel.objects, models.Manager)
        self.assertEqual(type(DefaultManagerTestModel.objects), models.Manager)

        # tag_objects should be TaggableManager
        self.assertIsInstance(DefaultManagerTestModel.tag_objects, TaggableManager)

    def test_custom_manager_preservation(self):
        """Test that custom managers are preserved while tag_objects is added."""
        from flexi_tag.tests.models import CustomManager, CustomManagerTestModel

        # Should have both objects and tag_objects managers
        self.assertTrue(hasattr(CustomManagerTestModel, "objects"))
        self.assertTrue(hasattr(CustomManagerTestModel, "tag_objects"))

        # objects should be the custom manager
        self.assertIsInstance(CustomManagerTestModel.objects, CustomManager)

        # tag_objects should be TaggableManager
        self.assertIsInstance(CustomManagerTestModel.tag_objects, TaggableManager)

        # Custom manager methods should work
        self.assertTrue(hasattr(CustomManagerTestModel.objects, "active"))
        self.assertTrue(hasattr(CustomManagerTestModel.objects, "inactive"))

    def test_existing_models_compatibility(self):
        """Test that existing models in the codebase still work correctly."""
        from flexi_tag.tests.models import ServiceTestModel, TaggableManagerTestModel

        # Both should have objects and tag_objects
        for model in [TaggableManagerTestModel, ServiceTestModel]:
            self.assertTrue(hasattr(model, "objects"))
            self.assertTrue(hasattr(model, "tag_objects"))

            # Should be able to use both managers
            self.assertIsInstance(model.objects, models.Manager)
            self.assertIsInstance(model.tag_objects, TaggableManager)

    def test_manager_functionality_works(self):
        """Test that both managers actually work for database operations."""
        from flexi_tag.tests.models import (
            CustomManagerTestModel,
            DefaultManagerTestModel,
        )

        # Test default manager model
        instance1 = DefaultManagerTestModel.objects.create(name="test1")
        self.assertEqual(DefaultManagerTestModel.objects.count(), 1)
        self.assertEqual(DefaultManagerTestModel.objects.get(name="test1"), instance1)

        # Test custom manager model
        instance2 = CustomManagerTestModel.objects.create(name="test2", is_active=True)
        instance3 = CustomManagerTestModel.objects.create(name="test3", is_active=False)

        # Test standard manager operations
        self.assertEqual(CustomManagerTestModel.objects.count(), 2)

        # Test custom manager methods
        active_objects = CustomManagerTestModel.objects.active()
        inactive_objects = CustomManagerTestModel.objects.inactive()

        self.assertEqual(active_objects.count(), 1)
        self.assertEqual(inactive_objects.count(), 1)
        self.assertEqual(active_objects.first(), instance2)
        self.assertEqual(inactive_objects.first(), instance3)

    def test_tag_objects_functionality(self):
        """Test that tag_objects manager provides tag-specific functionality."""
        from flexi_tag.tests.models import DefaultManagerTestModel

        # tag_objects should have tag-specific methods
        tag_manager = DefaultManagerTestModel.tag_objects

        # Should have tag-related methods
        self.assertTrue(hasattr(tag_manager, "filter_tag"))
        self.assertTrue(hasattr(tag_manager, "exclude_tag"))
        self.assertTrue(hasattr(tag_manager, "with_tags"))

    def test_multiple_inheritance_scenarios(self):
        """Test complex inheritance scenarios."""

        # Test model with multiple mixins
        class AnotherMixin(models.Model):
            created_at = models.DateTimeField(auto_now_add=True)

            class Meta:
                abstract = True

        class MultiMixinModel(AnotherMixin, FlexiTagMixin):
            name = models.CharField(max_length=100)

            class Meta:
                app_label = "tests"

        # Should still have both managers
        self.assertTrue(hasattr(MultiMixinModel, "objects"))
        self.assertTrue(hasattr(MultiMixinModel, "tag_objects"))
        self.assertIsInstance(MultiMixinModel.objects, models.Manager)
        self.assertIsInstance(MultiMixinModel.tag_objects, TaggableManager)

    def test_abstract_model_not_affected(self):
        """Test that abstract models are not affected by the metaclass."""

        class AbstractTestModel(FlexiTagMixin):
            name = models.CharField(max_length=100)

            class Meta:
                abstract = True

        # Abstract model should not be processed by metaclass
        # It might not have managers at all, which is fine
        # The important thing is that it doesn't cause errors

    def test_mixin_itself_not_affected(self):
        """Test that FlexiTagMixin itself is not affected by the metaclass."""

        # FlexiTagMixin should be abstract and not processed
        self.assertTrue(FlexiTagMixin._meta.abstract)

    def test_edge_case_custom_tag_objects(self):
        """Test edge case where user defines custom tag_objects."""

        class CustomTagManager(TaggableManager):
            def custom_method(self):
                return "custom"

        class CustomTagObjectsModel(FlexiTagMixin):
            name = models.CharField(max_length=100)
            tag_objects = CustomTagManager()

            class Meta:
                app_label = "tests"

        # Should preserve user's custom tag_objects
        self.assertIsInstance(CustomTagObjectsModel.tag_objects, CustomTagManager)
        self.assertTrue(hasattr(CustomTagObjectsModel.tag_objects, "custom_method"))

        # Should still have objects manager
        self.assertTrue(hasattr(CustomTagObjectsModel, "objects"))
        self.assertIsInstance(CustomTagObjectsModel.objects, models.Manager)
