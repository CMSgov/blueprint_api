import django_filters
from django.db.models import Q

from .models import Component


class ComponentFilter(django_filters.FilterSet):

    search = django_filters.CharFilter(method="keyword_search", label="Search")
    type = django_filters.CharFilter(lookup_expr="iexact")
    catalog = django_filters.NumberFilter()

    class Meta:
        model = Component
        fields = ["search", "type", "catalog"]

    def keyword_search(self, queryset, name, value):
        return queryset.filter(
            Q(title__icontains=value) | Q(description__icontains=value)
        )
