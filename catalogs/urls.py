from django.urls import path

from .views import CatalogListView, CatalogControlsView, CatalogControlDescriptionView

urlpatterns = [
    path("", CatalogListView.as_view(), name="catalog-list"),
    path("<int:catalog>/controls/all/", CatalogControlsView.as_view(), name="get_all_controls"),
    path(
        "<int:catalog>/control/<str:control_id>/", CatalogControlDescriptionView.as_view(), name="get_control_by_id",
    ),
]
