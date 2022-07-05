from django.urls import path

from .views import ProjectAddComponentView, ProjectsDetailView, ProjectsListViews

urlpatterns = [
    path("", ProjectsListViews.as_view(), name="project-list"),
    path("<int:project_id>/", ProjectsDetailView.as_view(), name="project-detail"),
    path(
        "<int:project_id>/add-component",
        ProjectAddComponentView.as_view(),
        name="project-add-component",
    ),
]
