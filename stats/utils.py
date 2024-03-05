"""
Various helper functions.
"""

import csv
import os
from io import BytesIO
from base64 import b64encode
from datetime import datetime
from PIL import Image, ImageDraw, ImageEnhance, ImageOps
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from stats.models import Game, PlayerStat, Pokemon, Teammate


def construct_game_context(game):
    """
    Create a context item to be interpreted by game_detail_base.html. It adds data for each team in the 'teams' key, the
    game's primary key in 'pk', as well as all the other Game fields.

    :param game: A Game object.
    :return: A dict containing the context needed by the template.
    """

    player_stats = game.playerstat_set.all().order_by("pseudo")  # Retrieve each player stat

    teams = [{}, {}]

    teams[0]["score"] = game.score_allies
    teams[1]["score"] = game.score_opponents
    mvp_vals = [0, 0]
    mvp_scores = [0, 0]
    mvp_ids = [-1, -1]

    idx = [0, 0]
    for stat in player_stats:
        team_id = 1 if stat.is_opponent else 0
        team = teams[team_id]

        stat_dict = {k: v for k, v in stat.__dict__.items() if not k.startswith("_")}
        stat_dict["pokemon"] = stat.pokemon
        stat_dict["is_mvp"] = False

        # MVP is the highest mark, or the highest scored points if there's a draw
        if stat_dict["result"] > mvp_vals[team_id] \
           or (stat_dict["result"] == mvp_vals[team_id] and stat_dict["scored"] > mvp_scores[team_id]):
            mvp_vals[team_id] = stat_dict["result"]
            mvp_scores[team_id] = stat_dict["scored"]
            mvp_ids[team_id] = idx[team_id]

        if "players" in team:
            team["players"].append(stat_dict)
        else:
            team["players"] = [stat_dict]

        idx[team_id] += 1

    for i, team in enumerate(teams):
        team["players"][mvp_ids[i]]["is_mvp"] = True

    return {
        "teams": teams,
        "pk": game.pk,
    } | {
        k: v for k, v in game.__dict__.items() if not k.startswith("_")
    }


def prefill_game(img, ocr_tool):
    """
    Get information about a game based on the screenshot of a game result.

    :param img: The screenshot that will be parsed.
    :param ocr_tool: The pyocr tool that will be used.
    :return: A dict containing the pre-filled information, and a preview image showing the bounding boxes.
    """

    text_boxes = {
        "ally_score": (766, 56, 904, 100),
        "opponent_score": (766, 372, 904, 416),
    }
    top = 115
    top_o = 433
    top_t = 110
    top_t_o = 428
    left = 688
    left_n = 929
    left_t = 1161
    tot_width = 36
    num_width = 62
    num_spacing = 75
    right = 916
    text_height = 30
    text_spacing = 53
    for i, h in enumerate(range(top, top+4*text_spacing+1, text_spacing)):
        text_boxes["ally_{}".format(i+1)] = (left, h, right, h+text_height)
        text_boxes["ally_{}_scored".format(i+1)] = (left_n, h, left_n+num_width, h+text_height)
        text_boxes["ally_{}_kills".format(i+1)] = (left_n+num_spacing, h,
                                                   left_n+num_width+num_spacing, h+text_height)
        text_boxes["ally_{}_assists".format(i+1)] = (left_n+2*num_spacing, h,
                                                     left_n+num_width+2*num_spacing, h+text_height)
    for i, h in enumerate(range(top_t, top_t+4*text_spacing+1, text_spacing)):
        text_boxes["ally_{}_total".format(i+1)] = (left_t, h,
                                                   left_t+tot_width, h+text_height)
    for i, h in enumerate(range(top_o, top_o+4*text_spacing+1, text_spacing)):
        text_boxes["opponent_{}".format(i + 1)] = (left, h, right, h + text_height)
        text_boxes["opponent_{}_scored".format(i+1)] = (left_n, h, left_n+num_width, h+text_height)
        text_boxes["opponent_{}_kills".format(i+1)] = (left_n+num_spacing, h,
                                                       left_n+num_width+num_spacing, h+text_height)
        text_boxes["opponent_{}_assists".format(i+1)] = (left_n+2 * num_spacing, h,
                                                         left_n+num_width+2*num_spacing, h+text_height)
    for i, h in enumerate(range(top_t_o, top_t_o+4*text_spacing+1, text_spacing)):
        text_boxes["opponent_{}_total".format(i+1)] = (left_t, h,
                                                       left_t+tot_width, h+text_height)

    result = {}

    pil_img = Image.open(img).convert("L")
    pil_img = ImageOps.invert(pil_img)
    pil_img = ImageEnhance.Contrast(pil_img).enhance(2)

    preview = pil_img.copy().convert("RGB")
    draw = ImageDraw.Draw(preview)
    output = BytesIO()

    for name, bb in text_boxes.items():
        cropped = pil_img.crop(bb)

        draw.rectangle(bb, outline=(255, 0, 0))

        result[name] = ocr_tool.image_to_string(cropped, lang="eng").strip()

    preview = preview.crop((600, 50, 1260, 684))
    preview.save(output, format='PNG')
    output.seek(0)
    preview_img = b64encode(output.read()).decode("ascii")

    return result, preview_img


def chunked(seq, chunksize):
    """
    Yields items from an iterator in list chunks.

    :param seq: Iterator.
    :param chunksize: Size of a chunk.
    """

    for pos in range(0, len(seq), chunksize):
        yield seq[pos:pos + chunksize]


@transaction.atomic
def bulk_import(csv_file, season):
    """
    Bulk import a csv web scraper dump into database.

    :param csv_file: An uploaded file that implements the .open() method.
    :param season: Season number.
    :return: Number of games added.
    """

    # Dictionary of Pokémon DB IDs, indexed by their name
    pokemons = {p.name.lower(): p.id for p in Pokemon.objects.all()}

    # Special cases, because uniteapi.dev doesn't have the same naming scheme as ours
    pokemons["meowscara"] = pokemons.pop("meowscarada")
    pokemons["ninetales"] = pokemons.pop("alolan ninetales")
    pokemons["mewtwox"] = pokemons.pop("mewtwo x")
    pokemons["mewtwoy"] = pokemons.pop("mewtwo y")
    pokemons["urshifu_rapid"] = pokemons.pop("urshifu")
    pokemons["urshifu_single"] = pokemons["urshifu_rapid"]
    pokemons["mrmime"] = pokemons.pop("mr. mime")

    # Load the csv into a list of rows
    rows = []
    with csv_file.open() as fp:
        csv_reader = csv.reader((line.decode() for line in fp))
        for row in csv_reader:
            rows.append(row)
    rows = rows[1:]  # Skip the header

    # 13 lines per game (2 for the result of each team, 10 player lines, and one empty line), + 1 for game metadata
    if not (len(rows) / 14).is_integer():
        raise ValueError("Line count should be a multiple of 14")
    num_games = int(len(rows) / 14)
    games_data = rows[:num_games * 13]
    games_metadata = rows[num_games * 13:]

    # Iterate over each game and create our objects
    for metadata, data in zip(games_metadata, chunked(games_data, 13)):
        # Process general information about the game, and assert which team is which
        is_won = not metadata[6].lower().startswith("l")
        is_forfeit = bool(metadata[7])
        team_a_won, team_a_score = data[0][2].split(" - ")
        team_a_won = team_a_won.lower().startswith("v")
        team_a_players = data[2:7]
        team_b_won, team_b_score = data[1][2].split(" - ")
        team_b_players = data[8:]

        # Check which team has the same result as our team, which is known from is_won
        if team_a_won == is_won:
            allies_score = team_a_score
            allies = team_a_players
            opponents_score = team_b_score
            opponents = team_b_players
        else:
            allies_score = team_b_score
            allies = team_b_players
            opponents_score = team_a_score
            opponents = team_a_players

        game = Game(
            is_won=is_won,
            is_forfeit=is_forfeit,
            date=datetime.strptime(metadata[8], "%d-%m-%Y %H:%M"),
            score_allies=allies_score,
            score_opponents=opponents_score,
            season=season
        )
        game.save()

        # Give a unique name to bots
        for i, p in enumerate(opponents):
            if p[3] == "BOT":  # FIXME let's hope the player named "BOT" doesn't come back one day
                p[3] = f"BOT_{i}"
                # FIXME we should implement a way of formally identifying bots in database

        # Process the PlayerStat entries associated with the current game
        for i, p in enumerate(allies + opponents):
            kills, assists, _ = (int(n) for n in p[5].split("|"))
            scored = p[4]

            # Try to identify the player's Pokémon based on the image url used in uniteapi.dev
            pkm_img = p[9]
            pkm_from_img = os.path.splitext(os.path.split(pkm_img)[1])[0].split("_")
            pkm_from_img = "_".join(pkm_from_img[pkm_from_img.index("Square") + 1:]).lower()
            try:
                found_pkm = Pokemon.objects.get(id=pokemons[pkm_from_img])
            except KeyError:
                raise ValueError(f"No pokémon found in {pkm_img}")

            # FIXME
            player_name = "Renn_Kane" if p[3] == "FCS_RennKane" else "AliceCheshir" if p[3] == "FCS_Alice" else p[3]
            is_ally = i < 5  # First five players are allies
            if is_ally:  # Check that the ally is a teammate
                try:
                    Teammate.objects.get(pseudo=player_name)
                except ObjectDoesNotExist:
                    raise ValueError(f"{player_name} n'est pas un teammate enregistré")

            ps = PlayerStat(
                game=game,
                pseudo=player_name,
                is_opponent=not is_ally,
                scored=scored,
                kills=kills,
                assists=assists,
                result=0,
                pokemon=found_pkm
            )
            print(ps)
            ps.save()

    return num_games
