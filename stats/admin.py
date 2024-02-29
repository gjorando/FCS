from functools import partialmethod

import pyocr
from django.contrib import admin
from django.http import HttpResponseRedirect
from django.urls import path
from django.template.response import TemplateResponse
from django.urls import reverse

from .forms import PlayerInlineAdminForm, PrefillForm, GameAdminForm, PokemonChoiceField
from .models import Game, PlayerStat, Teammate, Pokemon, Season
from .utils import prefill_game


DEFAULT_PLAYERS = ["Jejy", "AliceCheshir", "Leutik", "Helizen", "Renn_Kane"]
DEFAULT_POKEMONS = ["ZERAORA", "LUCARIO", "PIKACHU", "CRAMORANT", "SNORLAX"]


class PlayerInline(admin.TabularInline):
    """
    Inline for the players in a game. It displays exactly ten players when creating a game.
    """

    model = PlayerStat
    form = PlayerInlineAdminForm
    fieldsets = []
    extra = 10
    max_num = extra
    min_num = extra
    can_delete = False

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """
        Use a choice field for every available Pokémon, sorted by category.
        """

        if db_field.name == "pokemon":
            return PokemonChoiceField(queryset=Pokemon.objects.all())
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_formset(self, request, obj=None, **kwargs):
        """
        Fill each field of each player with either the prefill image data or default data.
        """

        initial = []
        formset = super(PlayerInline, self).get_formset(request, obj, **kwargs)

        if "prefilled_img" in request.session and not obj:
            prefill_data = request.session["prefilled_img"][0]
            for player_id in range(self.extra):
                prefix = f"ally_{player_id+1}" if player_id < 5 else f"opponent_{player_id-4}"

                # FIXME if we do not modify the default values, the entry is not created (it happens when a teammate
                # doesn't score/kills/assists, and uses the default pokémon)
                initial_values = {
                    "pseudo": prefill_data[prefix],
                    "scored": prefill_data[f"{prefix}_scored"],
                    "kills": prefill_data[f"{prefix}_kills"],
                    "assists": prefill_data[f"{prefix}_assists"],
                    "result": prefill_data[f"{prefix}_total"]
                }

                if player_id < 5:  # The 5 first entries are the ally team
                    try:
                        # TODO detect pokémons directly
                        initial_values["pokemon"] = DEFAULT_POKEMONS[DEFAULT_PLAYERS.index(prefill_data[prefix])]
                    except ValueError:
                        pass
                else:
                    initial_values["is_opponent"] = True

                initial.append(initial_values)
        elif not obj:
            for player_id in range(10):
                initial_values = {
                    "scored": 0,
                    "kills": 0,
                    "assists": 0,
                    "result": 10,
                }

                if player_id < 5:  # The 5 first entries are the allies team
                    # Pre-set the names of each player as well as their default Pokémon
                    initial_values["pseudo"] = DEFAULT_PLAYERS[player_id]
                    initial_values["pokemon"] = DEFAULT_POKEMONS[player_id]
                else:  # The 5 last are the opposing team
                    initial_values["is_opponent"] = True

                initial.append(initial_values)

        formset.__init__ = partialmethod(formset.__init__, initial=initial)
        return formset


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    """
    Custom admin for the Game model. It handles the automatic creation of 10 player fields when creating a new
    game, as well as the custom game prefill view.
    """

    form = GameAdminForm
    inlines = [PlayerInline]
    ordering = ("-date",)
    list_filter = ["season", "is_won"]
    list_display = ["date", "is_won", "score_allies", "score_opponents"]

    def get_urls(self):
        """
        Add a custom URL for game prefill in the list of available paths.
        """

        urls = super().get_urls()
        extra_urls = [
            path("prefill", self.admin_prefill, name="stats_game_prefill")
        ]

        return extra_urls + urls

    def render_change_form(self, request, context, *args, **kwargs):
        """
        Supplement the form with the prefill image if existing, and use a custom template that displays our extra URL.
        """

        self.change_form_template = 'stats/admin_game.html'

        extra_context = {}
        if "prefilled_img" in request.session and kwargs["add"]:
            extra_context["img"] = request.session["prefilled_img"]

        return super(GameAdmin, self).render_change_form(request, context | extra_context, *args, **kwargs)

    def get_changeform_initial_data(self, request):
        """
        Set the initial form data.
        """

        initial = super(GameAdmin, self).get_changeform_initial_data(request)

        # TODO use a table of defaults instead
        initial["season"] = Season.objects.latest()

        if "prefilled_img" in request.session:
            prefill_data = request.session["prefilled_img"][0]
            initial["score_allies"] = prefill_data["ally_score"]
            initial["score_opponents"] = prefill_data["opponent_score"]
            try:
                initial["is_won"] = int(prefill_data["ally_score"]) > int(prefill_data["opponent_score"])
            except ValueError:
                pass

        return initial

    def save_related(self, request, form, formsets, change):
        """
        During saving, delete the prefill image from the session object.
        """

        super(GameAdmin, self).save_related(request, form, formsets, change)
        if "prefilled_img" in request.session:
            del request.session["prefilled_img"]

    def admin_prefill(self, request):
        """
        Custom admin view that loads a result screenshot to prefill the admin Game form.
        """

        if "del" in request.GET:
            if "prefilled_img" in request.session:
                del request.session["prefilled_img"]
            return HttpResponseRedirect(reverse('admin:stats_game_add'))

        try:
            ocr_tool = pyocr.get_available_tools()[0]
        except IndexError:
            # FIXME use proper error page
            print("No OCR tool found")
            return HttpResponseRedirect(reverse('admin:stats_game_add'))

        if "eng" not in ocr_tool.get_available_languages():
            # FIXME use proper error page
            print("English is not available")
            return HttpResponseRedirect(reverse('admin:stats_game_add'))

        opts = Game._meta

        if request.method == "POST":
            prefill_form = PrefillForm(request.POST, request.FILES)
            if prefill_form.is_valid():
                raw_img = prefill_form.cleaned_data["picture"]
                request.session["prefilled_img"] = prefill_game(raw_img, ocr_tool)
                return HttpResponseRedirect(reverse('admin:stats_game_add'))
        else:
            prefill_form = PrefillForm()

        base_context = self.admin_site.each_context(request)
        context = base_context | {
            "title": "Pré-remplissage de partie",
            "opts": opts,
            "form": prefill_form,
        }

        return TemplateResponse(request, "stats/admin_prefill.html", context)


@admin.register(Pokemon)
class PokemonAdmin(admin.ModelAdmin):
    """
    Custom admin for the Pokemon mode.
    """

    ordering = ("category", "name",)

    def get_readonly_fields(self, request, obj=None):
        """
        Disallow the edition of the primary key on a Pokémon that already exists.
        """

        if obj:
            return ['id']
        else:
            return []


@admin.register(Teammate)
class TeammateAdmin(admin.ModelAdmin):
    """
    Custom admin for the Teammate model.
    """

    ordering = ("pseudo",)


@admin.register(Season)
class SeasonAdmin(admin.ModelAdmin):
    """
    Custom admin for the Season model.
    """

    ordering = ("-number",)

