import datetime
from django.shortcuts import render
from django.core.paginator import Paginator
from django.db.models import Count, Avg, Sum, Case, Value, When, FloatField, DateField
from django.db.models.functions import Cast, TruncDate
from django.http import HttpResponseRedirect
from django.urls import reverse

from .models import Game, PlayerStat, Teammate
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
    games_paginated = paginator.get_page(page_number)

    games_info = [utils.construct_game_context(game) for game in games_paginated]

    context = {
        "page_title": "Parties jouées",
        "games": games_info,
        "page_obj": games_paginated,  # This is needed for the paginator
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
        ally_stats = PlayerStat.objects.filter(is_opponent=False)

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
    num_games = len(games)

    # Compute win-rate per opponent
    # 9 parties, 5 gagnées
    per_opponent_winrate = opponent_stats.values("pokemon").annotate(
        winrate=100*Sum(
            Case(
                When(game__is_won=True, then=Value(1))
            ),
            output_field=FloatField()
        )/Cast(Count("pokemon"), FloatField()),
        num_games=Count("id")
    ).order_by("-winrate").exclude(winrate=None)

    # Compute averages per teammate
    per_ally_averages = ally_stats.values("pseudo").annotate(
        avg_scored=Avg("scored"),
        avg_kills=Avg("kills"),
        avg_assists=Avg("assists"),
        avg_result=Avg("result")
    ).order_by("-avg_result", "-avg_scored")

    # TODO refactoring

    avg_names = ("avg_scored", "avg_kills", "avg_assists", "avg_result")
    verbose_names = {
        "avg_scored": "Score moyen",
        "avg_kills": "Nombre moyen de kills",
        "avg_assists": "Nombre moyen d'assists",
        "avg_result": "Résultat moyen"
    }

    moving_averages = ally_stats.annotate(
        as_date=Cast(TruncDate("game__date"), output_field=DateField())
    ).values("as_date").annotate(
        avg_scored=Avg("scored"),
        avg_kills=Avg("kills"),
        avg_assists=Avg("assists"),
        avg_result=Avg("result")
    ).values("as_date", *avg_names).order_by("as_date")

    labels = []
    datasets = {}
    for point in moving_averages:
        date_label = str(point["as_date"])
        labels.append(date_label)
        for value_name in avg_names:
            if value_name in datasets:
                datasets[value_name].append(point[value_name])
            else:
                datasets[value_name] = [point[value_name]]

    color_values = {
        "avg_scored": "rgba(255,99,132,1)",
        "avg_kills": "rgba(54, 162, 235, 1)",
        "avg_assists": "rgba(255, 206, 86, 1)",
        "avg_result": "rgba(75, 192, 192, 1)"
    }

    # END TODO

    context = {
        "page_title": "Statistiques d'équipe",
        "win_percentage": winrate*100 if winrate else None,
        "num_games": num_games,
        "per_opponent_winrate": per_opponent_winrate,
        "per_ally_averages": per_ally_averages,
        "labels": labels,
        "datasets": datasets,
        "verbose_names": verbose_names,
        "color_values": color_values,
    }

    return render(request, "stats/team_stats.html", context)


def player_detail(request, pseudo):
    """
    Displays a number of stats for the player.

    :param request: Request object.
    :param pseudo: Player pseudo.
    """

    # FIXME implement filtering by season (see team_stats)
    # FIXME implement sliding window

    if len(Teammate.objects.values("pseudo").filter(pseudo=pseudo)) == 0:
        return HttpResponseRedirect(reverse('games_list'))

    player_stats = PlayerStat.objects.filter(is_opponent=False, pseudo=pseudo)

    averages = player_stats.aggregate(
        avg_scored=Avg("scored"),
        avg_kills=Avg("kills"),
        avg_assists=Avg("assists"),
        avg_result=Avg("result")
    )

    avg_names = ("avg_scored", "avg_kills", "avg_assists", "avg_result")
    verbose_names = {
        "avg_scored": "Score moyen",
        "avg_kills": "Nombre moyen de kills",
        "avg_assists": "Nombre moyen d'assists",
        "avg_result": "Résultat moyen"
    }
    moving_averages = player_stats.annotate(
        as_date=Cast(TruncDate("game__date"), output_field=DateField())
    ).values("as_date").annotate(
        avg_scored=Avg("scored"),
        avg_kills=Avg("kills"),
        avg_assists=Avg("assists"),
        avg_result=Avg("result")
    ).values("as_date", *avg_names).order_by("as_date")

    labels = []
    datasets = {}
    for point in moving_averages:
        date_label = str(point["as_date"])
        labels.append(date_label)
        for value_name in avg_names:
            if value_name in datasets:
                datasets[value_name].append(point[value_name])
            else:
                datasets[value_name] = [point[value_name]]

    color_values = {
        "avg_scored": "rgba(255,99,132,1)",
        "avg_kills": "rgba(54, 162, 235, 1)",
        "avg_assists": "rgba(255, 206, 86, 1)",
        "avg_result": "rgba(75, 192, 192, 1)"
    }

    context = {
        "page_title": "Statistiques de {}".format(pseudo),
        "pseudo": pseudo,
        "averages": averages,
        "labels": labels,
        "datasets": datasets,
        "verbose_names": verbose_names,
        "color_values": color_values,
    }

    return render(request, "stats/player_detail.html", context)
