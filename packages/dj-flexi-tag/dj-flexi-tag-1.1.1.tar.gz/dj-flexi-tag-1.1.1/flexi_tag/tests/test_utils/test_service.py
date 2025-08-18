try:
    from unittest import mock
except ImportError:
    import mock

from django.db.models import QuerySet
from django.test import TestCase

from flexi_tag.exceptions import TagNotFoundException, TagValidationException
from flexi_tag.tests.models import ServiceTestModel, ServiceTestModelTag
from flexi_tag.utils.service import TaggableService


class TaggableServiceTestCase(TestCase):
    def setUp(self):
        self.service = TaggableService()
        self.test_model = mock.MagicMock(spec=ServiceTestModel)
        self.test_model._meta.app_label = "tests"
        self.test_model.__class__.__name__ = "ServiceTestModel"

    def _setup_mock_tag_model(self, mock_get_tag_model_class):
        mock_tag_model = mock.MagicMock()
        mock_get_tag_model_class.return_value = mock_tag_model
        return mock_tag_model

    def _setup_mock_tag_instance(self, mock_tag_model, tags=None):
        mock_tag_instance = mock.MagicMock()
        mock_tag_instance.tags = tags if tags is not None else []
        mock_tag_model.objects.get_or_create.return_value = (mock_tag_instance, True)
        return mock_tag_instance

    def _setup_filter_with_instance(self, mock_tag_model, mock_tag_instance):
        mock_filter = mock.MagicMock()
        mock_filter.first.return_value = mock_tag_instance
        mock_tag_model.objects.filter.return_value = mock_filter

    @mock.patch("flexi_tag.utils.service.apps.get_model")
    def test_get_tag_model_class(self, mock_get_model):
        mock_get_model.return_value = ServiceTestModelTag

        result = TaggableService._TaggableService__get_tag_model_class(self.test_model)

        mock_get_model.assert_called_once_with("tests", "ServiceTestModelTag")
        self.assertEqual(result, ServiceTestModelTag)

    @mock.patch("flexi_tag.utils.service.apps.get_model")
    def test_get_tag_model_class_not_found(self, mock_get_model):
        mock_get_model.side_effect = LookupError()

        with self.assertRaises(ValueError) as context:
            TaggableService._TaggableService__get_tag_model_class(self.test_model)

        self.assertIn(
            "Tag model for tests.ServiceTestModel not found", str(context.exception)
        )
        self.assertIn(
            "Did you run 'python manage.py generate_tag_models'", str(context.exception)
        )

    def test_tag_key_validation(self):
        self.assertTrue(TaggableService._TaggableService__validate_tag_key("valid_key"))

        invalid_keys = [123, True, None, [], {}]
        for invalid_key in invalid_keys:
            with self.assertRaises(ValueError) as context:
                TaggableService._TaggableService__validate_tag_key(invalid_key)
            self.assertEqual(str(context.exception), "Tag key must be a string.")

    @mock.patch(
        "flexi_tag.utils.service.TaggableService._TaggableService__get_tag_model_class"
    )
    def test_add_tag(self, mock_get_tag_model_class):
        mock_tag_model = self._setup_mock_tag_model(mock_get_tag_model_class)
        mock_tag_instance = self._setup_mock_tag_instance(mock_tag_model)

        result = self.service.add_tag(self.test_model, "test_tag")

        mock_get_tag_model_class.assert_called_once_with(self.test_model)
        mock_tag_model.objects.get_or_create.assert_called_once_with(
            instance=self.test_model
        )
        self.assertEqual(mock_tag_instance.tags, ["test_tag"])
        mock_tag_instance.save.assert_called_once_with(update_fields=["tags"])
        self.assertEqual(result, self.test_model)

    @mock.patch(
        "flexi_tag.utils.service.TaggableService._TaggableService__get_tag_model_class"
    )
    def test_add_tag_already_exists(self, mock_get_tag_model_class):
        mock_tag_model = self._setup_mock_tag_model(mock_get_tag_model_class)
        mock_tag_instance = mock.MagicMock()
        mock_tag_instance.tags = ["existing_tag"]
        mock_tag_model.objects.get_or_create.return_value = (mock_tag_instance, False)

        with self.assertRaises(TagValidationException):
            self.service.add_tag(self.test_model, "existing_tag")

    @mock.patch(
        "flexi_tag.utils.service.TaggableService._TaggableService__get_tag_model_class"
    )
    def test_bulk_add_tags(self, mock_get_tag_model_class):
        mock_tag_model = self._setup_mock_tag_model(mock_get_tag_model_class)
        mock_tag_instance = self._setup_mock_tag_instance(mock_tag_model)

        result = self.service.bulk_add_tags(self.test_model, ["tag1", "tag2", "tag3"])

        mock_get_tag_model_class.assert_called_once_with(self.test_model)
        mock_tag_model.objects.get_or_create.assert_called_once_with(
            instance=self.test_model
        )
        self.assertEqual(mock_tag_instance.tags, ["tag1", "tag2", "tag3"])
        mock_tag_instance.save.assert_called_once_with(update_fields=["tags"])
        self.assertEqual(result, self.test_model)

    @mock.patch(
        "flexi_tag.utils.service.TaggableService._TaggableService__get_tag_model_class"
    )
    def test_bulk_add_tags_already_exists(self, mock_get_tag_model_class):
        mock_tag_model = self._setup_mock_tag_model(mock_get_tag_model_class)
        mock_tag_instance = mock.MagicMock()
        mock_tag_instance.tags = ["existing_tag"]
        mock_tag_model.objects.get_or_create.return_value = (mock_tag_instance, False)

        with self.assertRaises(TagValidationException):
            self.service.bulk_add_tags(self.test_model, ["new_tag", "existing_tag"])

    @mock.patch(
        "flexi_tag.utils.service.TaggableService._TaggableService__get_tag_model_class"
    )
    def test_bulk_operations_with_many_instances(self, mock_get_tag_model_class):
        mock_tag_model = self._setup_mock_tag_model(mock_get_tag_model_class)

        instance1 = mock.MagicMock()
        instance2 = mock.MagicMock()
        mock_queryset = mock.MagicMock(spec=QuerySet)
        mock_queryset.__getitem__.return_value = instance1
        mock_queryset.iterator.return_value = [instance1, instance2]

        mock_tag_instance1 = mock.MagicMock()
        mock_tag_instance1.tags = []
        mock_tag_instance2 = mock.MagicMock()
        mock_tag_instance2.tags = []

        mock_tag_model.objects.get_or_create.side_effect = [
            (mock_tag_instance1, True),
            (mock_tag_instance2, True),
        ]

        result = self.service.bulk_add_tags_with_many_instances(
            mock_queryset, ["tag1", "tag2"]
        )

        self.assertEqual(mock_get_tag_model_class.call_count, 1)
        self.assertEqual(mock_tag_model.objects.get_or_create.call_count, 2)
        self.assertEqual(mock_tag_instance1.save.call_count, 1)
        self.assertEqual(mock_tag_instance2.save.call_count, 1)
        self.assertEqual(result, mock_queryset)

        mock_get_tag_model_class.reset_mock()
        mock_tag_model.reset_mock()

        mock_tag_model = self._setup_mock_tag_model(mock_get_tag_model_class)
        mock_tag_instance = mock.MagicMock()
        mock_tag_instance.tags = ["existing_tag"]
        mock_tag_model.objects.get_or_create.return_value = (mock_tag_instance, False)

        with self.assertRaises(ValueError):
            self.service.bulk_add_tags_with_many_instances(
                mock_queryset, ["valid_tag", 123]
            )

        mock_get_tag_model_class.reset_mock()
        mock_tag_model.reset_mock()

        mock_tag_model = self._setup_mock_tag_model(mock_get_tag_model_class)
        mock_tag_instance = mock.MagicMock()
        mock_tag_instance.tags = ["existing_tag"]
        mock_tag_model.objects.get_or_create.return_value = (mock_tag_instance, False)

        with self.assertRaises(TagValidationException):
            self.service.bulk_add_tags_with_many_instances(
                mock_queryset, ["existing_tag"]
            )

    @mock.patch(
        "flexi_tag.utils.service.TaggableService._TaggableService__get_tag_model_class"
    )
    def test_remove_tag_success(self, mock_get_tag_model_class):
        mock_tag_model = self._setup_mock_tag_model(mock_get_tag_model_class)
        mock_tag_instance = mock.MagicMock()
        tags_list = ["tag_to_remove", "other_tag"]
        mock_tag_instance.tags = tags_list
        mock_tag_model.objects.filter.return_value.first.return_value = (
            mock_tag_instance
        )

        result = self.service.remove_tag(self.test_model, "tag_to_remove")

        mock_get_tag_model_class.assert_called_once_with(self.test_model)
        mock_tag_model.objects.filter.assert_called_once_with(instance=self.test_model)
        self.assertEqual(len(tags_list), 1)
        self.assertEqual(tags_list[0], "other_tag")
        mock_tag_instance.save.assert_called_once_with(update_fields=["tags"])
        self.assertEqual(result, mock_tag_instance)

    @mock.patch(
        "flexi_tag.utils.service.TaggableService._TaggableService__get_tag_model_class"
    )
    def test_remove_tag_error_cases(self, mock_get_tag_model_class):
        mock_tag_model = self._setup_mock_tag_model(mock_get_tag_model_class)

        mock_filter_none = mock.MagicMock()
        mock_filter_none.first.return_value = None
        mock_tag_model.objects.filter.return_value = mock_filter_none

        with self.assertRaises(TagNotFoundException):
            self.service.remove_tag(self.test_model, "any_tag")

        mock_get_tag_model_class.assert_called_with(self.test_model)
        mock_tag_model.objects.filter.assert_called_with(instance=self.test_model)

        mock_get_tag_model_class.reset_mock()
        mock_tag_model.objects.filter.reset_mock()

        mock_tag_instance = mock.MagicMock()
        mock_tag_instance.tags = ["tag1", "tag2"]
        mock_filter_with_tags = mock.MagicMock()
        mock_filter_with_tags.first.return_value = mock_tag_instance
        mock_tag_model.objects.filter.return_value = mock_filter_with_tags

        with self.assertRaises(TagValidationException):
            self.service.remove_tag(self.test_model, "non_existing_tag")

        mock_get_tag_model_class.assert_called_with(self.test_model)
        mock_tag_model.objects.filter.assert_called_with(instance=self.test_model)
        mock_tag_instance.save.assert_not_called()

    @mock.patch(
        "flexi_tag.utils.service.TaggableService._TaggableService__get_tag_model_class"
    )
    def test_bulk_remove_tags_scenarios(self, mock_get_tag_model_class):
        mock_tag_model = self._setup_mock_tag_model(mock_get_tag_model_class)
        tags_list = ["tag1", "tag2", "tag3"]
        mock_tag_instance = mock.MagicMock()
        mock_tag_instance.tags = tags_list
        mock_tag_model.objects.filter.return_value.first.return_value = (
            mock_tag_instance
        )

        keys = ["tag1", "tag3"]
        result = self.service.bulk_remove_tags(self.test_model, keys)

        mock_get_tag_model_class.assert_called_once_with(self.test_model)
        mock_tag_model.objects.filter.assert_called_once_with(instance=self.test_model)
        self.assertEqual(len(tags_list), 1)
        self.assertEqual(tags_list[0], "tag2")
        mock_tag_instance.save.assert_called_once_with(update_fields=["tags"])
        self.assertEqual(result, mock_tag_instance)

        mock_get_tag_model_class.reset_mock()
        mock_tag_model.reset_mock()

        mock_tag_model = self._setup_mock_tag_model(mock_get_tag_model_class)
        mock_tag_model.objects.filter.return_value.first.return_value = None

        with self.assertRaises(TagNotFoundException):
            self.service.bulk_remove_tags(self.test_model, ["tag1", "tag2"])

        mock_get_tag_model_class.assert_called_with(self.test_model)
        mock_tag_model.objects.filter.assert_called_with(instance=self.test_model)

        mock_get_tag_model_class.reset_mock()
        mock_tag_model.reset_mock()

        mock_tag_model = self._setup_mock_tag_model(mock_get_tag_model_class)
        mock_tag_instance = mock.MagicMock()
        mock_tag_instance.tags = mock.MagicMock()
        mock_tag_instance.tags.__contains__.side_effect = lambda key: key == "tag1"
        mock_tag_model.objects.filter.return_value.first.return_value = (
            mock_tag_instance
        )

        with self.assertRaises(TagValidationException):
            self.service.bulk_remove_tags(self.test_model, ["tag1", "non_existent_tag"])

    @mock.patch(
        "flexi_tag.utils.service.TaggableService._TaggableService__get_tag_model_class"
    )
    def test_bulk_remove_tags_with_many_instances(self, mock_get_tag_model_class):
        mock_tag_model = self._setup_mock_tag_model(mock_get_tag_model_class)

        instance1 = mock.MagicMock()
        instance2 = mock.MagicMock()
        mock_queryset = mock.MagicMock(spec=QuerySet)
        mock_queryset.__getitem__.return_value = instance1
        mock_queryset.iterator.return_value = [instance1, instance2]

        tags_list1 = ["tag1", "tag2"]
        mock_tag_instance1 = mock.MagicMock()
        mock_tag_instance1.tags = tags_list1

        tags_list2 = ["tag1", "tag3"]
        mock_tag_instance2 = mock.MagicMock()
        mock_tag_instance2.tags = tags_list2

        mock_tag_model.objects.filter.return_value.first.side_effect = [
            mock_tag_instance1,
            mock_tag_instance2,
        ]

        result = self.service.bulk_remove_tags_with_many_instances(
            mock_queryset, ["tag1"]
        )

        self.assertEqual(mock_get_tag_model_class.call_count, 1)
        self.assertEqual(mock_tag_model.objects.filter.call_count, 2)

        self.assertEqual(len(tags_list1), 1)
        self.assertEqual(tags_list1[0], "tag2")
        self.assertEqual(len(tags_list2), 1)
        self.assertEqual(tags_list2[0], "tag3")

        self.assertEqual(mock_tag_instance1.save.call_count, 1)
        self.assertEqual(mock_tag_instance2.save.call_count, 1)
        self.assertEqual(result, mock_queryset)

    @mock.patch(
        "flexi_tag.utils.service.TaggableService._TaggableService__get_tag_model_class"
    )
    def test_get_tags_scenarios(self, mock_get_tag_model_class):
        # Scenario 1: Getting existing tags
        mock_tag_model = self._setup_mock_tag_model(mock_get_tag_model_class)
        mock_tag_instance = mock.MagicMock()
        mock_tag_instance.tags = ["tag1", "tag2"]
        mock_tag_model.objects.get.return_value = mock_tag_instance

        result = self.service.get_tags(self.test_model)

        mock_get_tag_model_class.assert_called_once_with(self.test_model)
        mock_tag_model.objects.get.assert_called_once_with(instance=self.test_model)
        self.assertEqual(result, ["tag1", "tag2"])

        mock_get_tag_model_class.reset_mock()
        mock_tag_model.reset_mock()

        # Scenario 2: No tags found (returns empty list)
        mock_tag_model = self._setup_mock_tag_model(mock_get_tag_model_class)
        mock_tag_model.objects.get.return_value = None

        result = self.service.get_tags(self.test_model)

        mock_get_tag_model_class.assert_called_once_with(self.test_model)
        mock_tag_model.objects.get.assert_called_once_with(instance=self.test_model)
        self.assertEqual(result, [])

    def test_queryset_operations(self):
        mock_queryset = mock.MagicMock()
        mock_filtered_queryset = mock.MagicMock()
        mock_queryset.filter_tag.return_value = mock_filtered_queryset

        result = TaggableService.filter_by_tag(mock_queryset, "test_tag")

        mock_queryset.filter_tag.assert_called_once_with("test_tag")
        self.assertEqual(result, mock_filtered_queryset)

        mock_queryset = mock.MagicMock()
        mock_excluded_queryset = mock.MagicMock()
        mock_queryset.exclude_tag.return_value = mock_excluded_queryset

        result = TaggableService.exclude_by_tag(mock_queryset, "test_tag")

        mock_queryset.exclude_tag.assert_called_once_with("test_tag")
        self.assertEqual(result, mock_excluded_queryset)

        mock_queryset = mock.MagicMock()
        mock_prefetched_queryset = mock.MagicMock()
        mock_queryset.with_tags.return_value = mock_prefetched_queryset

        result = TaggableService.get_with_tags(mock_queryset)

        self.assertEqual(mock_queryset.with_tags.call_count, 1)
        self.assertEqual(result, mock_prefetched_queryset)

    @mock.patch("django.apps.apps.get_model")
    def test_add_and_remove_tag_flow(self, mock_get_model):
        mock_tag_model = mock.MagicMock()
        mock_get_model.return_value = mock_tag_model

        instance = ServiceTestModel(name="Test Integration")

        tags_list = []
        mock_tag_instance = mock.MagicMock()
        mock_tag_instance.tags = tags_list

        mock_tag_model.objects.get_or_create.return_value = (mock_tag_instance, True)
        mock_tag_model.objects.filter.return_value.first.return_value = (
            mock_tag_instance
        )

        self.service.add_tag(instance, "temp_tag")
        self.assertEqual(tags_list, ["temp_tag"])

        self.service.remove_tag(instance, "temp_tag")
        self.assertEqual(tags_list, [])

        mock_get_model.assert_called_with("tests", "ServiceTestModelTag")
        mock_tag_model.objects.get_or_create.assert_called_once_with(instance=instance)
        mock_tag_model.objects.filter.assert_called_once_with(instance=instance)
