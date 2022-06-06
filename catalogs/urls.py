from django.urls import path

from .views import getControlDescription

urlpatterns = [
    path(
        "<int:catalog>/<int:page>/<int:offset>",
        getControlDescription,
        name="get-control-data",
    ),
]
