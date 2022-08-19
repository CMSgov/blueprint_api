from django.urls import path

from .views import (
    ComponentDetailView,
    ComponentListSearchView,
    ComponentListView,
    ComponentNarrativeView,
    ComponentTypeListView,
)

urlpatterns = [
    path("", ComponentListView.as_view(), name="component-list"),
    path("<int:pk>/", ComponentDetailView.as_view(), name="component-detail"),
    path("search/", ComponentListSearchView.as_view(), name="component-search"),
    path("types/", ComponentTypeListView.as_view(), name="component-search"),
    path(
        "<int:pk>/narratives/",
        ComponentNarrativeView.as_view(),
        name="component-search",
    ),
]
