from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from flexi_tag.exceptions import (
    ObjectIDsNotDefinedException,
    TagNotDefinedException,
    TagNotFoundException,
)
from flexi_tag.utils.service import TaggableService


class TaggableViewSetMixin(object):
    taggable_service = TaggableService()

    @action(detail=True, methods=["post"])
    def add_tag(self, request, pk=None):
        obj = self.get_object()  # noqa
        key = request.data.get("key", None)

        if not key:
            raise TagNotDefinedException()

        self.taggable_service.add_tag(
            instance=obj,
            key=key,
        )
        return Response(status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"])
    def bulk_add_tag(self, request, pk=None):
        obj = self.get_object()  # noqa
        keys = request.data.get("keys", [])

        if not keys:
            raise TagNotDefinedException()

        self.taggable_service.bulk_add_tags(
            instance=obj,
            keys=keys,
        )
        return Response(status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"])
    def bulk_add_tags(self, request, pk=None):
        objs = request.data.get("objects", [])
        keys = request.data.get("keys", [])

        if not keys:
            raise TagNotDefinedException()
        if not objs:
            raise ObjectIDsNotDefinedException()

        objs = self.get_queryset().filter(id__in=objs)  # noqa

        self.taggable_service.bulk_add_tags_with_many_instances(
            instances=objs,
            keys=keys,
        )
        return Response(status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"])
    def remove_tag(self, request, pk=None):
        obj = self.get_object()  # noqa
        key = request.data.get("key")

        if not key:
            raise TagNotFoundException()

        self.taggable_service.remove_tag(
            instance=obj,
            key=key,
        )
        return Response(status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"])
    def bulk_remove_tags(self, request, pk=None):
        obj = self.get_object()  # noqa
        keys = request.data.get("keys", [])

        if not keys:
            raise TagNotDefinedException()

        self.taggable_service.bulk_remove_tags(
            instance=obj,
            keys=keys,
        )
        return Response(status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"])
    def bulk_remove_tags_with_many_instances(self, request, pk=None):
        objs = request.data.get("objects", [])
        keys = request.data.get("keys", [])

        if not keys:
            raise TagNotDefinedException()
        if not objs:
            raise ObjectIDsNotDefinedException()

        objs = self.get_queryset().filter(id__in=objs)  # noqa

        self.taggable_service.bulk_remove_tags_with_many_instances(
            instances=objs,
            keys=keys,
        )
        return Response(status=status.HTTP_200_OK)

    @action(detail=True, methods=["get"])
    def get_tags(self, request, pk=None):
        obj = self.get_object()
        tag_instance = self.taggable_service.get_tags(instance=obj)
        if not tag_instance:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(tag_instance, status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"])
    def filter_by_tag(self, request):
        key = request.query_params.get("key") or request.data.get("key")

        if not key:
            raise TagNotDefinedException()

        queryset = self.taggable_service.filter_by_tag(
            queryset=self.get_queryset(),  # noqa
            key=key,
        )

        page = self.paginate_queryset(queryset)  # noqa
        if page is not None:
            serializer = self.get_serializer(page, many=True)  # noqa
            return self.get_paginated_response(serializer.data)  # noqa

        serializer = self.get_serializer(queryset, many=True)  # noqa
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def exclude_by_tag(self, request):
        key = request.query_params.get("key") or request.data.get("key")

        if not key:
            raise TagNotDefinedException()

        queryset = self.taggable_service.exclude_by_tag(
            queryset=self.get_queryset(),  # noqa
            key=key,
        )

        page = self.paginate_queryset(queryset)  # noqa
        if page is not None:
            serializer = self.get_serializer(page, many=True)  # noqa
            return self.get_paginated_response(serializer.data)  # noqa

        serializer = self.get_serializer(queryset, many=True)  # noqa
        return Response(serializer.data)
