from django.urls import path

from .views import (
    ProjectAddComponentView,
    ProjectComponentListSearchView,
    ProjectRemoveComponentView,
    ProjectsDetailView,
    ProjectsListViews,
)

urlpatterns = [
    path("", ProjectsListViews.as_view(), name="project-list"),
    path("<int:project_id>/", ProjectsDetailView.as_view(), name="project-detail"),
    path(
        "add-component/",
        ProjectAddComponentView.as_view(),
        name="project-add-component",
    ),
    path(
        "remove-component/",
        ProjectRemoveComponentView.as_view(),
        name="project-remove-component",
    ),
    path(
        "<int:project_id>/search/",
        ProjectComponentListSearchView.as_view(),
        name="component-search",
    ),
]
