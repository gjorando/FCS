from django import template
from django.template.defaultfilters import stringfilter

from ..models import PlayerStat

register = template.Library()


@register.filter(name="pokemon_display", is_safe=True)
@stringfilter
def pokemon_display(value):
    """
    A simple filter to convert the pokemon storage id to its display name.
    """

    return PlayerStat(pokemon=value).get_pokemon_display()
