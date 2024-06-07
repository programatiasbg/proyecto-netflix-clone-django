from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login, name="login"),
    path("signup", views.signup, name="signup"),
    path("logout", views.logout, name="logout"),
    path("favorite", views.favorite, name="favorite"),
    path("search", views.search, name="search"),
    path("add-remove-favorite", views.add_remove_favorite, name="add-remove-favorite"),
    path("check-in-list", views.check_in_list, name="check-in-list"),
    path("movie/<str:pk>/", views.movie, name="movie"),
    path("genre/<str:genre>/", views.genre, name="genre"),
]
