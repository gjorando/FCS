"""
Various helper functions.
"""


def construct_game_context(game):
    """
    Create a context item to be interpreted by game_detail_base.html.

    :param game: A Game object.
    :return: A dict containing the context needed by the template.
    """

    player_stats = game.playerstat_set.all().order_by("-result")

    teams = [{}, {}]

    teams[0]["score"] = game.score_allies
    teams[1]["score"] = game.score_opponents

    for stat in player_stats:
        team = teams[1 if stat.is_opponent else 0]

        stat_dict = stat.__dict__
        stat_dict["pokemon"] = stat.get_pokemon_display()

        if "players" in team:
            team["players"].append(stat_dict)
        else:
            team["players"] = [stat_dict]

    return {
        "teams": teams,
        "pk": game.pk,
        "is_won": game.is_won,
        "date": game.date,
    }
