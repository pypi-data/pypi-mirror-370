try:
    from unittest import mock
except ImportError:
    import mock

from django.test import TestCase
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from flexi_tag.exceptions import (
    ObjectIDsNotDefinedException,
    TagNotDefinedException,
    TagNotFoundException,
)
from flexi_tag.tests.models import TaggableManagerTestModel
from flexi_tag.utils.views import TaggableViewSetMixin


class TestViewSet(TaggableViewSetMixin, ModelViewSet):
    queryset = TaggableManagerTestModel.objects.all()


class TaggableViewSetMixinTestCase(TestCase):
    def setUp(self):
        self.viewset = TestViewSet()
        self.viewset.format_kwarg = None
        self.viewset.taggable_service = mock.MagicMock()
        self.mock_object = mock.MagicMock(spec=TaggableManagerTestModel)
        self.viewset.get_object = mock.MagicMock(return_value=self.mock_object)

        # Mock the model class for the queryset
        self.mock_model_class = mock.MagicMock()
        self.mock_model_class.__name__ = "TaggableManagerTestModel"
        self.mock_model_class._meta.app_label = "tests"

        self.mock_queryset = mock.MagicMock()
        self.mock_queryset.model = self.mock_model_class
        self.mock_filtered_queryset = mock.MagicMock()
        self.mock_queryset.filter.return_value = self.mock_filtered_queryset
        self.viewset.get_queryset = mock.MagicMock(return_value=self.mock_queryset)

        self.viewset.paginate_queryset = mock.MagicMock(return_value=None)

        mock_serializer = mock.MagicMock()
        mock_serializer.data = {"data": "serialized_data"}
        self.viewset.get_serializer = mock.MagicMock(return_value=mock_serializer)

    def _create_mock_request(self, data=None, query_params=None):
        mock_request = mock.MagicMock()
        mock_request.data = data or {}
        mock_request.query_params = query_params or {}
        return mock_request

    def _setup_pagination(self, page=None):
        if page is None:
            page = [self.mock_object]

        self.viewset.paginate_queryset.return_value = page
        paginated_response = Response({"results": {"data": "serialized_data"}})
        self.viewset.get_paginated_response = mock.MagicMock(
            return_value=paginated_response
        )
        return paginated_response

    def test_tag_add_operations(self):
        mock_request = self._create_mock_request(data={"key": "test_tag"})

        response = self.viewset.add_tag(mock_request, pk=1)

        self.viewset.taggable_service.add_tag.assert_called_once_with(
            instance=self.mock_object,
            key="test_tag",
        )
        self.assertEqual(response.status_code, 200)

        mock_request = self._create_mock_request()

        with self.assertRaises(TagNotDefinedException):
            self.viewset.add_tag(mock_request, pk=1)

        mock_request = self._create_mock_request(data={"keys": ["tag1", "tag2"]})

        self.viewset.taggable_service.add_tag.reset_mock()
        response = self.viewset.bulk_add_tag(mock_request, pk=1)

        self.viewset.taggable_service.bulk_add_tags.assert_called_once_with(
            instance=self.mock_object,
            keys=["tag1", "tag2"],
        )
        self.assertEqual(response.status_code, 200)

        mock_request = self._create_mock_request()

        with self.assertRaises(TagNotDefinedException):
            self.viewset.bulk_add_tag(mock_request, pk=1)

    def test_bulk_add_tags_scenarios(self):
        mock_request = self._create_mock_request(
            data={"objects": [1, 2], "keys": ["tag1", "tag2"]}
        )

        response = self.viewset.bulk_add_tags(mock_request)

        self.mock_queryset.filter.assert_called_once_with(id__in=[1, 2])
        self.viewset.taggable_service.bulk_add_tags_with_many_instances.assert_called_once_with(
            instances=self.mock_filtered_queryset,
            keys=["tag1", "tag2"],
        )
        self.assertEqual(response.status_code, 200)

        mock_request = self._create_mock_request(data={"objects": [1, 2]})

        with self.assertRaises(TagNotDefinedException):
            self.viewset.bulk_add_tags(mock_request)

        mock_request = self._create_mock_request(data={"keys": ["tag1", "tag2"]})

        with self.assertRaises(ObjectIDsNotDefinedException):
            self.viewset.bulk_add_tags(mock_request)

    def test_tag_remove_operations(self):
        mock_request = self._create_mock_request(data={"key": "test_tag"})

        response = self.viewset.remove_tag(mock_request, pk=1)

        self.viewset.taggable_service.remove_tag.assert_called_once_with(
            instance=self.mock_object,
            key="test_tag",
        )
        self.assertEqual(response.status_code, 200)

        mock_request = self._create_mock_request()

        with self.assertRaises(TagNotFoundException):
            self.viewset.remove_tag(mock_request, pk=1)

        self.viewset.taggable_service.remove_tag.reset_mock()
        mock_request = self._create_mock_request(data={"keys": ["tag1", "tag2"]})

        response = self.viewset.bulk_remove_tags(mock_request, pk=1)

        self.viewset.taggable_service.bulk_remove_tags.assert_called_once_with(
            instance=self.mock_object,
            keys=["tag1", "tag2"],
        )
        self.assertEqual(response.status_code, 200)

        mock_request = self._create_mock_request()

        with self.assertRaises(TagNotDefinedException):
            self.viewset.bulk_remove_tags(mock_request, pk=1)

    def test_bulk_remove_tags_with_many_instances_scenarios(self):
        mock_request = self._create_mock_request(
            data={"objects": [1, 2], "keys": ["tag1", "tag2"]}
        )

        response = self.viewset.bulk_remove_tags_with_many_instances(mock_request)

        self.mock_queryset.filter.assert_called_once_with(id__in=[1, 2])
        self.viewset.taggable_service.bulk_remove_tags_with_many_instances.assert_called_once_with(
            instances=self.mock_filtered_queryset,
            keys=["tag1", "tag2"],
        )
        self.assertEqual(response.status_code, 200)

        mock_request = self._create_mock_request(data={"objects": [1, 2]})

        with self.assertRaises(TagNotDefinedException):
            self.viewset.bulk_remove_tags_with_many_instances(mock_request)

        mock_request = self._create_mock_request(data={"keys": ["tag1", "tag2"]})

        with self.assertRaises(ObjectIDsNotDefinedException):
            self.viewset.bulk_remove_tags_with_many_instances(mock_request)

    def test_get_tags_scenarios(self):
        mock_request = self._create_mock_request()

        tag_instance = {"tags": ["tag1", "tag2"]}
        self.viewset.taggable_service.get_tags.return_value = tag_instance

        response = self.viewset.get_tags(mock_request, pk=1)

        self.viewset.taggable_service.get_tags.assert_called_once_with(
            instance=self.mock_object,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, tag_instance)

        mock_request = self._create_mock_request()

        self.viewset.taggable_service.get_tags.reset_mock()
        self.viewset.taggable_service.get_tags.return_value = None

        response = self.viewset.get_tags(mock_request, pk=1)

        self.viewset.taggable_service.get_tags.assert_called_once_with(
            instance=self.mock_object,
        )
        self.assertEqual(response.status_code, 404)

    @mock.patch("flexi_tag.utils.service.apps.get_model")
    def test_filter_by_tag_scenarios(self, mock_get_model):
        # Mock the tag model
        mock_tag_model = mock.MagicMock()
        mock_get_model.return_value = mock_tag_model
        mock_request = self._create_mock_request(query_params={"key": "test_tag"})

        # Mock TaggableService instance method
        with mock.patch.object(
            self.viewset.taggable_service, "filter_by_tag"
        ) as mock_filter_by_tag:
            mock_filter_by_tag.return_value = self.mock_filtered_queryset

            response = self.viewset.filter_by_tag(mock_request)

            mock_filter_by_tag.assert_called_once_with(
                queryset=self.mock_queryset,
                key="test_tag",
            )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {"data": "serialized_data"})

        mock_request = self._create_mock_request()

        with self.assertRaises(TagNotDefinedException):
            self.viewset.filter_by_tag(mock_request)

        mock_request = self._create_mock_request(query_params={"key": "test_tag"})

        page = [self.mock_object]
        paginated_response = self._setup_pagination(page)

        with mock.patch.object(
            self.viewset.taggable_service, "filter_by_tag"
        ) as mock_filter_by_tag:
            mock_filter_by_tag.return_value = self.mock_filtered_queryset

            response = self.viewset.filter_by_tag(mock_request)

            self.viewset.paginate_queryset.assert_called_with(
                self.mock_filtered_queryset
            )
            self.viewset.get_serializer.assert_called_with(page, many=True)
            self.viewset.get_paginated_response.assert_called_with(
                {"data": "serialized_data"}
            )
            self.assertEqual(response, paginated_response)

    @mock.patch("flexi_tag.utils.service.apps.get_model")
    def test_exclude_by_tag_scenarios(self, mock_get_model):
        # Mock the tag model
        mock_tag_model = mock.MagicMock()
        mock_get_model.return_value = mock_tag_model
        mock_request = self._create_mock_request(query_params={"key": "test_tag"})

        # Mock TaggableService instance method
        with mock.patch.object(
            self.viewset.taggable_service, "exclude_by_tag"
        ) as mock_exclude_by_tag:
            mock_exclude_by_tag.return_value = self.mock_filtered_queryset

            response = self.viewset.exclude_by_tag(mock_request)

            mock_exclude_by_tag.assert_called_once_with(
                queryset=self.mock_queryset,
                key="test_tag",
            )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {"data": "serialized_data"})

        mock_request = self._create_mock_request()

        with self.assertRaises(TagNotDefinedException):
            self.viewset.exclude_by_tag(mock_request)

        mock_request = self._create_mock_request(query_params={"key": "test_tag"})

        page = [self.mock_object]
        paginated_response = self._setup_pagination(page)

        with mock.patch.object(
            self.viewset.taggable_service, "exclude_by_tag"
        ) as mock_exclude_by_tag:
            mock_exclude_by_tag.return_value = self.mock_filtered_queryset

            response = self.viewset.exclude_by_tag(mock_request)

            self.viewset.paginate_queryset.assert_called_with(
                self.mock_filtered_queryset
            )
            self.viewset.get_serializer.assert_called_with(page, many=True)
            self.viewset.get_paginated_response.assert_called_with(
                {"data": "serialized_data"}
            )
            self.assertEqual(response, paginated_response)
