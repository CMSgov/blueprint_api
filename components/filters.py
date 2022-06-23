import django_filters

from .models import Component


class ComponentFilter(django_filters.FilterSet):
    class Meta:
        model = Component
        ordering = ["-id"]
        fields = {
            "type": ["exact", "in"],
            "catalog": ["exact", "in"],
        }
