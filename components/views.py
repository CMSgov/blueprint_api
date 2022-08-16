from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import QuerySet
from django_filters import rest_framework as filters
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.request import Request

from components.filters import ComponentFilter, ComponentPermissionsFilter
from components.models import Component
from components.permissions import ComponentPermissions
from components.serializers import ComponentListSerializer, ComponentSerializer


class ComponentListView(generics.ListCreateAPIView):
    """Use for read-write endpoints to represent a collection of model instances.
    Provides get and post method handlers.
    """
    queryset = Component.objects.all()
    serializer_class = ComponentListSerializer
    permission_classes = [ComponentPermissions, ]
    filter_backends = [ComponentPermissionsFilter, ]

    def filter_queryset(self, queryset: QuerySet) -> QuerySet:
        # Need to apply the order_by after the union in ComponentPermissionsFilter
        return super().filter_queryset(queryset).order_by("pk")


class ComponentDetailView(generics.RetrieveAPIView):
    """
    Use for read or update endpoints to represent a single model instance.
    Provides get, put, and patch method handlers.
    """
    queryset = Component.objects.all()
    permission_classes = [ComponentPermissions, ]
    serializer_class = ComponentSerializer


class ComponentListSearchView(generics.ListAPIView):
    queryset = Component.objects.exclude(status=Component.Status.SYSTEM).order_by("pk")
    permission_classes = [ComponentPermissions, ]
    filterset_class = ComponentFilter
    filter_backends = [filters.DjangoFilterBackend, ]
    serializer_class = ComponentListSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page_number = self.request.query_params.get("page", default=1)

        paginator = Paginator(queryset, 20)
        try:
            page_obj = paginator.page(page_number)
        except PageNotAnInteger:
            page_obj = paginator.page(1)
        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages)

        serializer = self.get_serializer(page_obj, many=True)
        response = serializer.data
        response.append({"total_item_count": paginator.count})

        return Response(response, status=status.HTTP_200_OK)


class ComponentTypeListView(generics.ListAPIView):
    queryset = Component.objects.values_list("type")
    permission_classes = [ComponentPermissions, ]
    filter_backends = [ComponentPermissionsFilter, ]

    def list(self, request: Request, *args, **kwargs) -> Response:
        queryset = self.filter_queryset(self.get_queryset())

        return Response(queryset, status=status.HTTP_200_OK)
