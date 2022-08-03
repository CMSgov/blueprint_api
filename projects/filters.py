import django_filters

from .models import Control


class ControlsFilter(django_filters.FilterSet):
    status = django_filters.CharFilter(lookup_expr="iexact")
    responsibility = django_filters.CharFilter(lookup_expr="iexact")

    class Meta:
        model = Control
        fields = ["status", "responsibility"]
