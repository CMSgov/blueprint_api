from rest_framework import serializers

from .models import Catalog, Controls


class CatalogListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Catalog
        fields = (
            "id",
            "name",
            "file_name",
            "source",
            "version",
            "impact_level",
        )


class ControlSerializer(serializers.ModelSerializer):
    class Meta:
        model = Controls
        fields = "__all__"
