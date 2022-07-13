from django.urls import path

from .views import CatalogListView, get_all_controls, get_control_by_id

urlpatterns = [
    path("", CatalogListView.as_view(), name="catalog-list"),
    path("<int:catalog>/controls/all/", get_all_controls, name="get_all_controls"),
    path(
        "<int:catalog>/control/<str:control_id>/",
        get_control_by_id,
        name="get_control_by_id",
    ),
]
