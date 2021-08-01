from django.shortcuts import render
from django.core.paginator import Paginator
from .models import Game
from . import utils


def games_list(request):
    """
    Main view that displays the list of games.

    :param request: Request object.
    """

    page_number = request.GET.get("page")
    try:
        items_per_page = int(request.GET.get("per_page"))
    except TypeError:
        items_per_page = 10

    games = Game.objects.all().order_by("-date")

    paginator = Paginator(games, items_per_page)
    games = paginator.get_page(page_number)

    games_info = [utils.construct_game_context(game) for game in games]

    context = {
        "page_title": "Parties jouées",
        "games": games_info,
        "page_obj": games,
        "items_per_page": items_per_page,
    }

    return render(request, "stats/games_list.html", context)


def game_detail(request, game_id):
    """
    Displays the details of a given game.

    :param request: Request object.
    :param game_id: Primary key associated to the game.
    """

    game = Game.objects.get(pk=game_id)

    context = {
        "page_title": str(game),
        "game": utils.construct_game_context(game),
    }

    return render(request, "stats/game_detail.html", context)
