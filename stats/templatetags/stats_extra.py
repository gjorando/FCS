from django import template
from django.template.defaultfilters import stringfilter
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe

from ..models import PlayerStat

register = template.Library()


@register.filter(name="pokemon_display", is_safe=True)
@stringfilter
def pokemon_display(value):
    """
    A simple filter to convert the pokemon storage id to its display name.
    """

    return PlayerStat(pokemon=value).get_pokemon_display()


@register.filter(name="get_item", needs_autoescape=True)
def get_item(dictionary, key, autoescape=True):
    if autoescape:
        esc = conditional_escape
    else:
        esc = lambda x: x
    return mark_safe(esc(dictionary.get(key)))
