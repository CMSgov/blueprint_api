from rest_framework import serializers

from projects.models import Project


class ProjectSerializer(serializers.ModelSerializer):
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
        )
