import django_filters

from .models import Control


class ControlsFilter(django_filters.FilterSet):
    status = django_filters.AllValuesMultipleFilter(
        field_name="status",
        lookup_expr="in",
    )
    responsibility = django_filters.AllValuesMultipleFilter(
        field_name="responsibility",
        lookup_expr="in",
    )

    class Meta:
        model = Control
        fields = ["status", "responsibility"]
