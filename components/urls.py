from django.urls import path

from .views import ComponentDetailView, ComponentListView

urlpatterns = [
    path("", ComponentListView.as_view(), name="component-list"),
    path("<int:pk>/", ComponentDetailView.as_view(), name="component-detail"),
]
