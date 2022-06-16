from rest_framework import serializers

from components.models import Component


class ComponentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Component
        fields = (
            "id",
            "title",
            "description",
            "type",
            "catalog",
            "controls",
            "search_terms",
            "component_json",
        )
