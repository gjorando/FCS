"""
Various helper functions.
"""

from io import BytesIO
from base64 import b64encode
from PIL import Image, ImageDraw, ImageEnhance, ImageOps
import pytesseract


def construct_game_context(game):
    """
    Create a context item to be interpreted by game_detail_base.html.

    :param game: A Game object.
    :return: A dict containing the context needed by the template.
    """

    # TODO display MVP
    player_stats = game.playerstat_set.all().order_by("-scored", "-result", "-pseudo")

    teams = [{}, {}]

    teams[0]["score"] = game.score_allies
    teams[1]["score"] = game.score_opponents

    for stat in player_stats:
        team = teams[1 if stat.is_opponent else 0]

        stat_dict = stat.__dict__

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


def prefill_game(img):
    """
    Get information about a game based on the screenshot of a game result.

    :param img: The screenshot that will be parsed.
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

        result[name] = pytesseract.image_to_string(cropped).strip()

    preview = preview.crop((600, 50, 1260, 684))
    preview.save(output, format='PNG')
    output.seek(0)
    preview_img = b64encode(output.read()).decode("ascii")

    return result, preview_img
