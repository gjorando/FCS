from django import template
from django.template.defaultfilters import stringfilter
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe

from ..models import Pokemon

register = template.Library()


@register.filter(name="pokemon_display", is_safe=True)
def pokemon_display(value):
    """
    A simple filter to convert the pokemon storage id to its display name.
    """

    if isinstance(value, Pokemon):
        return value.name
    else:
        return Pokemon.objects.get(id=value).name


@register.filter(name="get_item", needs_autoescape=True)
def get_item(dictionary, key, autoescape=True):
    if autoescape:
        esc = conditional_escape
    else:
        def esc(x): return x
    return mark_safe(esc(dictionary.get(key)))
