from django.shortcuts import render
from .models import Game

def games_list(request):
    """
    Main view that displays the list of games.
    """


    context = {
        "page_title": "Parties jouées",
        "games": Game.objects.all().order_by("-date")
    }

    return render(request, "stats/games_list.html", context)

def game_detail(request, game_id):
    """
    Displays the details of a given game.
    """

    game = Game.objects.get(pk=game_id)

    context = {
        "page_title": str(game),
        "game": game,
        "players": game.player_set.all(),
    }

    return render(request, "stats/game_detail.html", context)