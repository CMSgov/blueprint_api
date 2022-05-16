from django.urls import path

from .views import UsersDetailView, UsersListViews

urlpatterns = [
    path("", UsersListViews.as_view()),
    path("<int:user_id>/", UsersDetailView.as_view()),
]
