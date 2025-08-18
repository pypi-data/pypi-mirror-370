try:
    from unittest import mock
except ImportError:
    import mock

from django.db import models
from django.db.models import Q
from django.test import TestCase

from flexi_tag.tests.models import TaggableManagerTestModel
from flexi_tag.utils.compat import JSONField
from flexi_tag.utils.model_managers import TaggableManager
from flexi_tag.utils.models import FlexiTagMixin


class TaggableManagerTestModelTag(models.Model):
    """Test model tag for basic TaggableManager tests."""

    instance = models.OneToOneField(
        "tests.TaggableManagerTestModel",
        on_delete=models.CASCADE,
        primary_key=True,
    )
    tags = JSONField(default=list)

    class Meta:
        app_label = "tests"


class TaggableManagerComplexTestModelTag(models.Model):
    """Test model tag for advanced TaggableManager tests."""

    instance = models.OneToOneField(
        "tests.TaggableManagerTestModel",
        on_delete=models.CASCADE,
        primary_key=True,
    )
    tags = JSONField(default=list)

    class Meta:
        app_label = "tests"


class TaggableManagerTestCase(TestCase):
    def setUp(self):
        self.manager = TaggableManager()
        self.manager.model = TaggableManagerTestModel

    def _mock_queryset_setup(
        self,
        mock_get_tag_model_class_name=None,
        use_complex_tag=False,
    ):
        tag_model_name = "TaggableManagerTestModelTag"
        if use_complex_tag:
            tag_model_name = "TaggableManagerComplexTestModelTag"

        if mock_get_tag_model_class_name:
            mock_get_tag_model_class_name.return_value = tag_model_name

        mock_queryset = mock.MagicMock()
        mock_filtered_queryset = mock.MagicMock()
        mock_queryset.filter.return_value = mock_filtered_queryset
        mock_queryset.exclude.return_value = mock_filtered_queryset
        self.manager.get_queryset = mock.MagicMock(return_value=mock_queryset)

        return mock_queryset, mock_filtered_queryset, tag_model_name

    def test_tag_model_validation_methods(self):
        # Test Case 1: Successful validation of tag model class
        with mock.patch(
            "flexi_tag.utils.model_managers.apps.get_model"
        ) as mock_get_model:
            mock_get_model.return_value = TaggableManagerTestModelTag

            result = self.manager._TaggableManager__validate_tag_model_class(
                "tests", "TaggableManagerTestModelTag"
            )

            mock_get_model.assert_called_once_with(
                "tests", "TaggableManagerTestModelTag"
            )
            self.assertEqual(result, TaggableManagerTestModelTag)

        # Test Case 2: Model class not found
        with mock.patch(
            "flexi_tag.utils.model_managers.apps.get_model"
        ) as mock_get_model:
            mock_get_model.side_effect = LookupError()

            with self.assertRaises(ValueError) as context:
                self.manager._TaggableManager__validate_tag_model_class(
                    "tests", "NonExistentModel"
                )

            self.assertIn(
                "Tag model for tests.NonExistentModel not found.",
                str(context.exception),
            )
            self.assertIn(
                "Did you run 'python manage.py generate_tag_models'",
                str(context.exception),
            )

        # Test Case 3: Getting tag model class name
        with mock.patch(
            "flexi_tag.utils.model_managers.TaggableManager._TaggableManager__validate_tag_model_class"
        ) as mock_validate:
            mock_validate.return_value = TaggableManagerTestModelTag

            result = self.manager._TaggableManager__get_tag_model_class_name(
                TaggableManagerTestModel
            )

            self.assertEqual(result, "TaggableManagerTestModelTag")
            mock_validate.assert_called_once_with(
                app_label="tests", tag_model_name="TaggableManagerTestModelTag"
            )

        # Test Case 4: Recursive validation of tag model class
        with mock.patch(
            "flexi_tag.utils.model_managers.apps.get_model"
        ) as mock_get_model:
            mock_get_model.return_value = TaggableManagerComplexTestModelTag

            result = self.manager._TaggableManager__validate_tag_model_class(
                "tests", "TaggableManagerComplexTestModelTag"
            )

            mock_get_model.assert_called_once_with(
                "tests", "TaggableManagerComplexTestModelTag"
            )
            self.assertEqual(result, TaggableManagerComplexTestModelTag)

        # Test Case 5: Handling nested model classes
        class OuterTestModel:
            class InnerTestModel(FlexiTagMixin):
                class Meta:
                    app_label = "tests"

        self.manager._TaggableManager__validate_tag_model_class = mock.MagicMock()

        result = self.manager._TaggableManager__get_tag_model_class_name(
            OuterTestModel.InnerTestModel
        )

        self.assertEqual(result, "InnerTestModelTag")
        self.manager._TaggableManager__validate_tag_model_class.assert_called_once_with(
            app_label="tests", tag_model_name="InnerTestModelTag"
        )

    def test_basic_query_operations(self):
        # Test Case 1: Filter by tag
        with mock.patch(
            "flexi_tag.utils.model_managers.TaggableManager._TaggableManager__get_tag_model_class_name"
        ) as mock_get_tag_model_class_name:
            (
                mock_queryset,
                mock_filtered_queryset,
                tag_model_name,
            ) = self._mock_queryset_setup(
                mock_get_tag_model_class_name=mock_get_tag_model_class_name
            )

            result = self.manager.filter_tag("test_tag")

            mock_get_tag_model_class_name.assert_called_once_with(
                TaggableManagerTestModel
            )
            key = "{tag_model_name}__tags__contains".format(
                tag_model_name=tag_model_name,
            )
            mock_queryset.filter.assert_called_once_with(**{key: ["test_tag"]})
            self.assertEqual(result, mock_filtered_queryset)

        # Test Case 2: Exclude by tag
        with mock.patch(
            "flexi_tag.utils.model_managers.TaggableManager._TaggableManager__get_tag_model_class_name"
        ) as mock_get_tag_model_class_name:
            (
                mock_queryset,
                mock_filtered_queryset,
                tag_model_name,
            ) = self._mock_queryset_setup(
                mock_get_tag_model_class_name=mock_get_tag_model_class_name
            )

            result = self.manager.exclude_tag("test_tag")

            mock_get_tag_model_class_name.assert_called_once_with(
                TaggableManagerTestModel
            )
            key = "{tag_model_name}__tags__contains".format(
                tag_model_name=tag_model_name,
            )
            mock_queryset.exclude.assert_called_once_with(**{key: ["test_tag"]})
            self.assertEqual(result, mock_filtered_queryset)

        # Test Case 3: With tags (prefetch_related)
        with mock.patch(
            "flexi_tag.utils.model_managers.TaggableManager._TaggableManager__get_tag_model_class_name"
        ) as mock_get_tag_model_class_name:
            mock_get_tag_model_class_name.return_value = "TaggableManagerTestModelTag"
            mock_queryset = mock.MagicMock()
            mock_prefetched_queryset = mock.MagicMock()
            mock_queryset.prefetch_related.return_value = mock_prefetched_queryset
            self.manager.get_queryset = mock.MagicMock(return_value=mock_queryset)

            result = self.manager.with_tags()

            mock_get_tag_model_class_name.assert_called_once_with(
                TaggableManagerTestModel
            )
            mock_queryset.prefetch_related.assert_called_once_with(
                "TaggableManagerTestModelTag"
            )
            self.assertEqual(result, mock_prefetched_queryset)

    def test_advanced_query_operations(self):
        # Test Case 1: Filtering with Q objects
        with mock.patch(
            "flexi_tag.utils.model_managers.TaggableManager._TaggableManager__get_tag_model_class_name"
        ) as mock_get_tag_model_class_name:
            mock_get_tag_model_class_name.return_value = (
                "TaggableManagerComplexTestModelTag"
            )
            mock_queryset = mock.MagicMock()
            mock_filtered_queryset = mock.MagicMock()
            mock_q_filtered_queryset = mock.MagicMock()

            mock_queryset.filter.return_value = mock_filtered_queryset
            mock_filtered_queryset.filter.return_value = mock_q_filtered_queryset

            self.manager.get_queryset = mock.MagicMock(return_value=mock_queryset)

            q_object = Q(status="active")

            filtered_queryset = self.manager.filter_tag("test_tag")
            result = filtered_queryset.filter(q_object)

            mock_get_tag_model_class_name.assert_called_once_with(
                TaggableManagerTestModel
            )

            expected_filter = "TaggableManagerComplexTestModelTag__tags__contains"
            self.assertEqual(mock_queryset.filter.call_count, 1)
            call_kwargs = mock_queryset.filter.call_args[1]
            self.assertIn(expected_filter, call_kwargs)
            self.assertEqual(call_kwargs[expected_filter], ["test_tag"])

            self.assertEqual(mock_filtered_queryset.filter.call_count, 1)
            args = mock_filtered_queryset.filter.call_args[0]
            self.assertTrue(any(isinstance(arg, Q) for arg in args))

            self.assertEqual(result, mock_q_filtered_queryset)

        # Test Case 2: Excluding with Q objects
        with mock.patch(
            "flexi_tag.utils.model_managers.TaggableManager._TaggableManager__get_tag_model_class_name"
        ) as mock_get_tag_model_class_name:
            mock_get_tag_model_class_name.return_value = (
                "TaggableManagerComplexTestModelTag"
            )
            mock_queryset = mock.MagicMock()
            mock_excluded_queryset = mock.MagicMock()
            mock_q_excluded_queryset = mock.MagicMock()

            mock_queryset.exclude.return_value = mock_excluded_queryset
            mock_excluded_queryset.filter.return_value = mock_q_excluded_queryset

            self.manager.get_queryset = mock.MagicMock(return_value=mock_queryset)

            q_object = Q(status="inactive")

            excluded_queryset = self.manager.exclude_tag("test_tag")
            result = excluded_queryset.filter(q_object)

            mock_get_tag_model_class_name.assert_called_once_with(
                TaggableManagerTestModel
            )

            expected_filter = "TaggableManagerComplexTestModelTag__tags__contains"
            self.assertEqual(mock_queryset.exclude.call_count, 1)
            call_kwargs = mock_queryset.exclude.call_args[1]
            self.assertIn(expected_filter, call_kwargs)
            self.assertEqual(call_kwargs[expected_filter], ["test_tag"])

            self.assertEqual(mock_excluded_queryset.filter.call_count, 1)
            args = mock_excluded_queryset.filter.call_args[0]
            self.assertTrue(any(isinstance(arg, Q) for arg in args))

            self.assertEqual(result, mock_q_excluded_queryset)

        # Test Case 3: Chaining select_related with with_tags
        with mock.patch(
            "flexi_tag.utils.model_managers.TaggableManager._TaggableManager__get_tag_model_class_name"
        ) as mock_get_tag_model_class_name:
            mock_get_tag_model_class_name.return_value = (
                "TaggableManagerComplexTestModelTag"
            )
            mock_queryset = mock.MagicMock()
            mock_prefetched_queryset = mock.MagicMock()
            mock_select_related_queryset = mock.MagicMock()

            mock_queryset.prefetch_related.return_value = mock_prefetched_queryset
            mock_prefetched_queryset.select_related.return_value = (
                mock_select_related_queryset
            )

            self.manager.get_queryset = mock.MagicMock(return_value=mock_queryset)

            result = self.manager.with_tags().select_related("some_related_field")

            mock_get_tag_model_class_name.assert_called_once_with(
                TaggableManagerTestModel
            )
            mock_queryset.prefetch_related.assert_called_once_with(
                "TaggableManagerComplexTestModelTag"
            )
            mock_prefetched_queryset.select_related.assert_called_once_with(
                "some_related_field"
            )
            self.assertEqual(result, mock_select_related_queryset)

    def test_integration_scenarios(self):
        # Test Case 1: Filter tag integration
        with mock.patch("django.apps.apps.get_model") as mock_get_model:
            mock_tag_model = mock.MagicMock()
            mock_get_model.return_value = mock_tag_model

            manager = TaggableManager()
            manager.model = TaggableManagerTestModel

            mock_queryset = mock.MagicMock()
            mock_filtered_queryset = mock.MagicMock()
            mock_queryset.filter.return_value = mock_filtered_queryset
            manager.get_queryset = mock.MagicMock(return_value=mock_queryset)

            result = manager.filter_tag("test_tag")

            self.assertEqual(result, mock_filtered_queryset)
            self.assertEqual(mock_queryset.filter.call_count, 1)

        # Test Case 2: Exclude tag integration
        with mock.patch("django.apps.apps.get_model") as mock_get_model:
            mock_tag_model = mock.MagicMock()
            mock_get_model.return_value = mock_tag_model

            manager = TaggableManager()
            manager.model = TaggableManagerTestModel

            mock_queryset = mock.MagicMock()
            mock_excluded_queryset = mock.MagicMock()
            mock_queryset.exclude.return_value = mock_excluded_queryset
            manager.get_queryset = mock.MagicMock(return_value=mock_queryset)

            result = manager.exclude_tag("test_tag")

            self.assertEqual(result, mock_excluded_queryset)
            self.assertEqual(mock_queryset.exclude.call_count, 1)

        # Test Case 3: With tags integration
        with mock.patch("django.apps.apps.get_model") as mock_get_model:
            mock_tag_model = mock.MagicMock()
            mock_get_model.return_value = mock_tag_model

            manager = TaggableManager()
            manager.model = TaggableManagerTestModel

            mock_queryset = mock.MagicMock()
            mock_prefetched_queryset = mock.MagicMock()
            mock_queryset.prefetch_related.return_value = mock_prefetched_queryset
            manager.get_queryset = mock.MagicMock(return_value=mock_queryset)

            result = manager.with_tags()

            self.assertEqual(result, mock_prefetched_queryset)
            self.assertEqual(mock_queryset.prefetch_related.call_count, 1)
