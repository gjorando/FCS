from django.urls import path
from . import views

urlpatterns = [
    path("", views.games_list, name="games_list"),
    path("game/<int:game_id>", views.game_detail, name="game_detail"),
]