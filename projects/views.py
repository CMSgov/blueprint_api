from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Q, Count
from django.shortcuts import get_object_or_404
from django_filters import rest_framework as filters
from guardian.shortcuts import get_objects_for_user
from rest_framework import generics, status
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from blueprintapi.filters import ObjectPermissionsFilter
from components.filters import ComponentFilter
from components.models import Component
from components.serializers import ComponentListBasicSerializer
from projects.filters import ProjectControlFilter
from projects.models import Project, ProjectControl
from projects.permissions import ProjectControlPermissions
from projects.serializers import (
    ProjectControlSerializer,
    ProjectListSerializer,
    ProjectSerializer, ProjectControlListSerializer,
)

n_completed = Count("to_project", filter=Q(to_project__status="complete"))
total_controls = Count("to_project")

project_queryset = (
    Project.objects.annotate(completed_controls=n_completed).annotate(total_controls=total_controls).order_by("pk")
)


class ProjectsListViews(generics.ListCreateAPIView):
    queryset = project_queryset
    serializer_class = ProjectListSerializer
    filter_backends = [
        ObjectPermissionsFilter,
    ]


class ProjectsDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = project_queryset
    serializer_class = ProjectSerializer
    lookup_url_kwarg = "project_id"


class ProjectAddComponentView(generics.GenericAPIView):
    queryset = Project.objects.all()

    def post(self, request, *args, **kwargs):
        project = get_object_or_404(Project, pk=request.data.get("project_id"))
        self.check_object_permissions(request, project)

        component_id = int(request.data.get("component_id"))
        component = get_object_or_404(Component, pk=component_id)

        if project.catalog.id == component.catalog.id:
            project.components.add(component.id)
            response = {
                "message": f"{component.title} and {len(component.controls)} control narratives successfully added to {project.title}."
            }
            return Response(response, status=status.HTTP_200_OK)

        return Response(
            {"response": "Incompatible catalog selected"},
            status=status.HTTP_400_BAD_REQUEST,
        )


class ProjectRemoveComponentView(generics.GenericAPIView):
    queryset = Project.objects.all()

    def post(self, request, *args, **kwargs):
        project = get_object_or_404(Project, pk=request.data.get("project_id"))
        self.check_object_permissions(request, project)

        component = get_object_or_404(
            Component, pk=int(request.data.get("component_id"))
        )

        if not project.components.contains(component):
            return Response(
                {
                    "message": f"{component.title} is not associated with"
                    " {project.title} and cannot be removed."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        project.components.remove(component.id)

        return Response(
            {
                "message": f"{component.title} and {len(component.controls)} control narratives successfully removed from {project.title}."
            },
            status=status.HTTP_200_OK,
        )


class ProjectComponentListSearchView(generics.GenericAPIView):
    queryset = Project.objects.all()
    lookup_url_kwarg = "project_id"

    def get(self, request, *args, **kwargs):
        project_instance = self.get_object()
        page_number = self.request.query_params.get("page", default=1)

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


class ProjectComponentNotAddedListView(generics.GenericAPIView):
    queryset = Project.objects.all()
    lookup_url_kwarg = "project_id"
    serializer_class = ComponentListBasicSerializer

    def get(self, request, *args, **kwargs):
        project_instance = self.get_object()

        queryset = (
            Component.objects.exclude(used_by_projects=project_instance)
            .exclude(status=1)
            .order_by("pk")
        )

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ProjectGetControlList(generics.ListAPIView):
    serializer_class = ProjectControlListSerializer
    filterset_class = ProjectControlFilter
    filter_backends = (filters.DjangoFilterBackend,)
    pagination_class = PageNumberPagination

    def get_queryset(self):
        user = self.request.user
        queryset = get_objects_for_user(user, "projects.view_project", Project.objects.all(), accept_global_perms=False)
        project = get_object_or_404(queryset, pk=self.kwargs.get("project_id"))

        return ProjectControl.objects.filter(project=project)


class RetrieveUpdateProjectControlView(generics.RetrieveUpdateAPIView):
    queryset = ProjectControl.objects.all()
    serializer_class = ProjectControlSerializer
    lookup_url_kwarg = "project_id"
    permission_classes = [ProjectControlPermissions, ]

    def get_serializer_context(self) -> dict:
        return {"control_id": self.kwargs.get("control_id"), **super().get_serializer_context()}

    def get_object(self) -> ProjectControl:
        project = get_object_or_404(Project, pk=self.kwargs.get("project_id"))
        self.check_object_permissions(self.request, project)

        return get_object_or_404(ProjectControl, control__control_id=self.kwargs.get("control_id"), project=project)
