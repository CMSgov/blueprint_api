from django.urls import path

from .views import get_all_controls, get_control_by_id

urlpatterns = [
    path("<int:catalog>/controls/all/", get_all_controls, name="get_all_controls"),
    path(
        "<int:catalog>/control/<str:control_id>/",
        get_control_by_id,
        name="get-control-data",
    ),
]
