from django.db.models import Q
from django_filters import rest_framework as filters

from .models import Component


class ComponentFilter(filters.FilterSet):

    search = filters.CharFilter(method="keyword_search", label="Search")
    type = filters.CharFilter(lookup_expr="iexact")
    catalog = filters.NumberFilter()

    class Meta:
        model = Component
        fields = ["search", "type", "catalog"]

    def keyword_search(self, queryset, name, value):
        return queryset.filter(
            Q(title__icontains=value) | Q(description__icontains=value)
        )
