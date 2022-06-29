from rest_framework import serializers

from components.serializers import ComponentListSerializer
from projects.models import Project


class ProjectSerializer(serializers.ModelSerializer):
    components = ComponentListSerializer(many=True)
    components_count = serializers.SerializerMethodField()

    def get_components_count(self, obj):
        return obj.components.count()

    class Meta:
        model = Project
        fields = (
            "id",
            "title",
            "acronym",
            "impact_level",
            "location",
            "status",
            "creator",
            "components",
            "components_count",
        )
        depth = 1
