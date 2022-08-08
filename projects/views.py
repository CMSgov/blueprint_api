from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from components.filters import ComponentFilter
from components.models import Component
from components.serializers import ComponentListBasicSerializer

from .filters import ControlsFilter
from .models import Control, Project
from .serializers import (
    ControlsListSerializer,
    ProjectControlSerializer,
    ProjectListSerializer,
    ProjectSerializer,
)


class ProjectsListViews(generics.ListCreateAPIView):

    queryset = Project.objects.all().order_by("pk")
    serializer_class = ProjectListSerializer

    def list(self, request, *args, **kwargs):
        projects = self.get_queryset()
        serializer = ProjectListSerializer(projects, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ProjectsDetailView(APIView):
    def get_object(self, project_id):
        try:
            return Project.objects.get(id=project_id)
        except Project.DoesNotExist:
            return None

    def get(self, request, project_id, *args, **kwargs):
        project_instance = get_object_or_404(Project, pk=project_id)
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
    def post(self, request, *args, **kwargs):
        project = get_object_or_404(Project, pk=request.data.get("project_id"))
        owner_id = project.creator.id

        creator_id = int(request.data.get("creator"))
        if owner_id != creator_id:
            return Response(
                {"response": "You are not authorized to access this page"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        component_id = int(request.data.get("component_id"))
        component = get_object_or_404(Component, pk=component_id)

        if project.catalog.id == component.catalog.id:
            project.components.add(component.id)
            response = {"message": f"{component.title} added to {project.title}."}
            return Response(response, status=status.HTTP_200_OK)
        return Response(
            {"response": "Incompatable catalog selected"},
            status=status.HTTP_400_BAD_REQUEST,
        )


class ProjectRemoveComponentView(APIView):
    def post(self, request, *args, **kwargs):
        project = get_object_or_404(Project, pk=request.data.get("project_id"))
        component = get_object_or_404(
            Component, pk=int(request.data.get("component_id"))
        )
        owner_id = project.creator.pk
        creator_id = int(request.data.get("creator"))
        if owner_id != creator_id:
            return Response(
                {"response": "You are not authorized to access this page"},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        try:
            project.components.remove(component.id)
            response = {"message": f"{component.title} removed from {project.title}."}
        except Exception:
            return Response({}, status=status.HTTP_400_BAD_REQUEST)
        return Response(response, status=status.HTTP_200_OK)


class ProjectGetControlList(APIView):
    def get(self, request, project_id):
        page_number = request.query_params.get("page", default=1)
        filtered_qs = ControlsFilter(
            request.GET,
            queryset=Control.objects.filter(project_id=project_id).order_by(
                "control_id"
            ),
        ).qs

        paginator = Paginator(filtered_qs, 20)
        try:
            page_obj = paginator.page(page_number)
        except PageNotAnInteger:
            page_obj = paginator.page(1)
        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages)

        serializer_class = ControlsListSerializer
        serializer = serializer_class(page_obj, many=True)
        project = Project.objects.get(pk=project_id)
        project_serializer = ProjectListSerializer(project)
        response = {
            "controls": serializer.data,
            "project_data": project_serializer.data,
            "total_item_count": paginator.count,
        }

        return Response(response, status=status.HTTP_200_OK)


class ProjectGetControlData(APIView):
    def get(self, request, project_id, control_id):
        project_instance = get_object_or_404(Project, pk=project_id)
        serlializer = ProjectControlSerializer(
            project_instance,
            context={
                "control_id": control_id,
            },
        )

        return Response(serlializer.data, status=status.HTTP_200_OK)


class ProjectComponentListSearchView(APIView):
    def get(self, request, project_id, *args, **kwargs):
        page_number = self.request.query_params.get("page", default=1)
        project_instance = get_object_or_404(Project, pk=project_id)

        filtered_qs = ComponentFilter(
            self.request.GET,
            queryset=project_instance.components.all().order_by("pk"),
        ).qs
        paginator = Paginator(filtered_qs, 20)
        try:
            page_obj = paginator.page(page_number)
        except PageNotAnInteger:
            page_obj = paginator.page(1)
        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages)

        serializer_class = ComponentListBasicSerializer
        serializer = serializer_class(page_obj, many=True)
        project_serializer = ProjectListSerializer(project_instance, many=False)

        type_list = (
            project_instance.components.all().order_by().values_list("type").distinct()
        )

        response = {
            "project": project_serializer.data,
            "components": serializer.data,
            "total_item_count": paginator.count,
            "type_list": type_list,
        }

        return Response(response, status=status.HTTP_200_OK)


class ProjectComponentNotAddedListView(APIView):
    def get(self, request, project_id, *args, **kwargs):
        project_instance = get_object_or_404(Project, pk=project_id)
        queryset = (
            Component.objects.exclude(used_by_projects=project_instance)
            .exclude(status=1)
            .order_by("pk")
        )
        serializer = ComponentListBasicSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
