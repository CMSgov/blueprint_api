from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from components.models import Component

from .models import Project
from .serializers import ProjectSerializer


class ProjectsListViews(APIView):

    # @api_view('POST')
    def post(self, request, *args, **kwargs):
        serializer = ProjectSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # @api_view('GET')
    def get(request, *args, **kwargs):
        projects = Project.objects.all()
        serializer = ProjectSerializer(projects, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ProjectsDetailView(APIView):
    def get_object(self, project_id):
        try:
            return Project.objects.get(id=project_id)
        except Project.DoesNotExist:
            return None

    def get(self, request, project_id, *args, **kwargs):
        project_instance = self.get_object(project_id)
        if not project_instance:
            return Response(
                {"response": "The project you are looking for does not exist"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer = ProjectSerializer(project_instance)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, project_id, *args, **kwargs):
        project_instance = self.get_object(project_id)
        if not project_instance:
            return Response(
                {"response": "The project you are looking for does not exist"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer = ProjectSerializer(
            instance=project_instance, data=request.data, partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, project_id, *args, **kwargs):
        project_instance = self.get_object(project_id)
        if not project_instance:
            return Response(
                {"response": "The project you are looking for does not exist"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        project_instance.delete()
        return Response(
            {"response": "You have succesfully deleted the project!"},
            status=status.HTTP_200_OK,
        )


class ProjectAddComponentView(APIView):
    def get_object(self, project_id):
        try:
            return Project.objects.get(id=project_id)
        except Project.DoesNotExist:
            return None

    def get_component_object(self, component_id):
        try:
            return Component.objects.get(pk=component_id)
        except Component.DoesNotExist:
            return None

    def post(self, request, project_id, *args, **kwargs):
        # Make sure project is valid
        projectExists = self.get_object(project_id)
        if projectExists is None:
            return Response(
                {"response": "The project you are looking for does not exist"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        # check user is for this project
        projectOwnerId = projectExists.creator.pk
        passedInCreatorId = int(request.data.get("creator"))
        if projectOwnerId != passedInCreatorId:
            return Response(
                {"response": "You are not authorized to access this page"},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        # Make sure that the component is valid
        passedInComponentId = int(request.data.get("component_id"))
        componentExists = self.get_component_object(passedInComponentId)
        # componentExists = Component.objects.get(pk=passedInComponentId)
        if componentExists is None:
            return Response(
                {"response": "The selected component does not exist"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        # Check component catalog mataches project catalog
        if projectExists.catalog.id == componentExists.catalog.id:
            # Connect the component to the project
            projectExists.components.add(componentExists)
            projectExists.save()
            return Response({}, status=status.HTTP_200_OK)
        return Response(
            {"response": "Incompatable catalog selected"},
            status=status.HTTP_400_BAD_REQUEST,
        )
