from django.urls import path

from .views import (
    ProjectAddComponentView,
    ProjectComponentListSearchView,
    ProjectComponentNotAddedListView,
    ProjectGetControlList,
    ProjectRemoveComponentView,
    ProjectSspDownloadView,
    ProjectsDetailView,
    ProjectsListViews,
    RetrieveUpdateProjectControlView,
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
        "<int:project_id>/controls/",
        ProjectGetControlList.as_view(),
        name="project-get-control",
    ),
    path(
        "<int:project_id>/controls/<str:control_id>/",
        RetrieveUpdateProjectControlView.as_view(),
        name="project-get-control",
    ),
    path(
        "<int:project_id>/search/",
        ProjectComponentListSearchView.as_view(),
        name="component-search",
    ),
    path(
        "<int:project_id>/components-not-added/",
        ProjectComponentNotAddedListView.as_view(),
        name="components-not-in-project",
    ),
    path(
        "<int:project_id>/download/oscal",
        ProjectSspDownloadView.as_view({"get": "download"}),
        name="download-ssp",
    ),
]
