from django.contrib import admin
from django.http import HttpResponseRedirect
from django.urls import path
from django.template.response import TemplateResponse
from django.urls import reverse

from .forms import PlayerInlineAdminForm, PrefillForm, GameAdminForm, PokemonChoiceField
from .models import Game, PlayerStat, Teammate, Pokemon
from .utils import prefill_game


class PlayerInline(admin.TabularInline):
    """
    Displays exactly ten players when creating a game.
    """

    model = PlayerStat
    form = PlayerInlineAdminForm
    fieldsets = []
    extra = 10
    max_num = 10
    min_num = 10
    can_delete = False

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "pokemon":
            return PokemonChoiceField(queryset=Pokemon.objects.all())
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    """
    Register an admin entry for the Game table.
    """

    form = GameAdminForm
    inlines = [PlayerInline]
    ordering = ("-date",)
    list_filter = ["season", "is_won"]
    list_display = ["date", "is_won", "score_allies", "score_opponents"]

    def get_urls(self):
        urls = super().get_urls()
        extra_urls = [
            path("prefill", self.admin_prefill, name="stats_game_prefill"),
        ]

        return extra_urls + urls

    def render_change_form(self, request, context, *args, **kwargs):
        self.change_form_template = 'stats/admin_game.html'

        # print(args, kwargs)

        extra_context = {}
        if "prefilled_img" in request.session and kwargs["add"]:
            extra_context["img"] = request.session["prefilled_img"][1]
            # FIXME
            del request.session["prefilled_img"]

        return super(GameAdmin, self).render_change_form(request, context | extra_context, *args, **kwargs)

    def get_form(self, request, obj=None, change=False, **kwargs):
        form = super(GameAdmin, self).get_form(request, obj, change, **kwargs)

        # FIXME understand how to set the initial values
        #print(form().as_p())
        if not change:
            pass
            #print("NEW")
        else:
            pass
            #print("UPDATE")

        return form

    def admin_prefill(self, request):
        """
        Loads a result screenshot to prefill the admin Game form.
        """

        opts = Game._meta

        if request.method == "POST":
            prefill_form = PrefillForm(request.POST, request.FILES)
            if prefill_form.is_valid():
                raw_img = prefill_form.cleaned_data["picture"]
                request.session["prefilled_img"] = prefill_game(raw_img)
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
    ordering = ("category", "name",)

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ['id']
        else:
            return []


@admin.register(Teammate)
class TeammateAdmin(admin.ModelAdmin):
    ordering = ("pseudo",)
