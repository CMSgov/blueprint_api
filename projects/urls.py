from django.urls import path

from .views import ProjectsDetailView, ProjectsListViews

urlpatterns = [
    path("", ProjectsListViews.as_view(), name="project-list"),
    path("<int:project_id>/", ProjectsDetailView.as_view(), name="project-detail"),
]
