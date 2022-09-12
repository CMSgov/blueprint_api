from django.db.models import Q
from django_filters import rest_framework as filters
from guardian.shortcuts import get_objects_for_user
from rest_framework.filters import BaseFilterBackend

from components.models import Component


class ComponentFilter(filters.FilterSet):

    search = filters.CharFilter(method="keyword_search", label="Search")
    type = filters.CharFilter(lookup_expr="iexact")
    catalog_version = filters.CharFilter(field_name="supported_catalog_versions", lookup_expr="contains")

    class Meta:
        model = Component
        fields = ["search", "type"]

    def keyword_search(self, queryset, name, value):  # pylint: disable=unused-argument
        return queryset.filter(
            Q(title__icontains=value) | Q(description__icontains=value)
        )


class ComponentPermissionsFilter(BaseFilterBackend):
    """A filter backend that limits results to those where the requesting user
    has read object level permissions.
    """
    perm_format = '%(app_label)s.view_%(model_name)s'

    def filter_queryset(self, request, queryset, view):
        user = request.user
        permission = self.perm_format % {
            'app_label': queryset.model._meta.app_label,
            'model_name': queryset.model._meta.model_name,
        }

        return (
            get_objects_for_user(user, permission, queryset, accept_global_perms=False)
            .union(queryset.filter(status=Component.Status.PUBLIC))
        )
