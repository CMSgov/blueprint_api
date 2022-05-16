from django.urls import path

from .views import (
    ProjectsListViews,
    ProjectsDetailView
)

urlpatterns = [
    path("", ProjectsListViews.as_view()),
    path("/<int:project_id>/", ProjectsDetailView.as_view()),
]
