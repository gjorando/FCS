from django.shortcuts import render
from django.core.paginator import Paginator
from django.db.models import Count, Avg, Sum, Case, Value, When, FloatField
from django.db.models.functions import Cast
from .models import Game, PlayerStat
from . import utils
from .forms import GamesListFilterForm


def games_list(request):
    """
    Main view that displays the list of games.

    :param request: Request object.
    """

    page_number = request.GET.get("page")

    if request.method == "GET":
        filter_form = GamesListFilterForm(request.GET)
        filter_form.is_valid()
        items_per_page = filter_form.cleaned_data.get("per_page") or 10
        season_filter = filter_form.cleaned_data.get("season") or None
    else:
        items_per_page = 10
        season_filter = None

    url_get_encode = request.GET.copy()
    if "page" in url_get_encode:
        url_get_encode.pop("page")
    url_get_encode = url_get_encode.urlencode()

    filter_form = GamesListFilterForm(initial={
        "per_page": items_per_page,
        "season": season_filter
    })

    if season_filter:
        games = Game.objects.filter(season=season_filter).order_by("-date")
    else:
        games = Game.objects.all().order_by("-date")

    paginator = Paginator(games, items_per_page)
    games = paginator.get_page(page_number)

    games_info = [utils.construct_game_context(game) for game in games]

    context = {
        "page_title": "Parties jouées",
        "games": games_info,
        "page_obj": games,
        "url_get_encode": url_get_encode,
        "filter_form": filter_form,
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


def team_stats(request):
    """
    Displays a number of stats for the team.

    :param request: Request object.
    """

    topn = 5

    if request.method == "GET":
        # FIXME implement filtering by season
        season_filter = None
    else:
        season_filter = None

    if season_filter:
        # FIXME see above
        pass
    else:
        games = Game.objects.all()
        opponent_stats = PlayerStat.objects.filter(is_opponent=True)

    # Compute winrate
    winrate = games.aggregate(
        winrate=Avg(
            Case(
                When(is_won=True, then=Value(1)),
                When(is_won=False, then=Value(0))
            ),
            output_field=FloatField()
        )
    )["winrate"]

    # Compute win-rate per opponent
    # 9 parties, 5 gagnées
    per_opponent_winrate = opponent_stats.values("pokemon") \
        .annotate(
        winrate=100*Sum(
            Case(
                When(game__is_won=True, then=Value(1))
            ),
            output_field=FloatField()
        )/Cast(Count("pokemon"), FloatField())
    ).order_by("-winrate").exclude(winrate=None)

    context = {
        "page_title": "Statistiques d'équipe",
        "win_percentage": winrate*100,
        "per_opponent_winrate": per_opponent_winrate,
    }

    return render(request, "stats/team_stats.html", context)
