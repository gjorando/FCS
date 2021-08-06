from base64 import b64encode
from django.contrib import admin
from django.http import HttpResponseRedirect
from django.urls import path
from django.template.response import TemplateResponse
from django.urls import reverse

from .forms import PlayerInlineAdminForm, PrefillForm
from .models import Game, PlayerStat, Teammate
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


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    """
    Register an admin entry for the Game table..
    """

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

    def get_queryset(self, request):
        # FIXME https://stackoverflow.com/questions/7513384/pass-initial-value-to-a-modelform-in-django
        # https://stackoverflow.com/questions/727928/django-admin-how-to-access-the-request-object-in-admin-py-for-list-display-met
        # https://stackoverflow.com/questions/51155947/django-redirect-to-another-view-with-context/51156032
        qs = super(GameAdmin, self).get_queryset(request)
        self.request = request
        return qs

    def render_change_form(self, request, context, *args, **kwargs):
        self.change_form_template = 'stats/admin_game.html'

        extra_context = {}
        if "prefilled_img" in request.session:
            extra_context["img"] = request.session["prefilled_img"][1]
            extra_context["prefill_data"] = request.session["prefilled_img"][0]
            #del request.session["prefilled_img"]

        return super(GameAdmin, self).render_change_form(request, context | extra_context, *args, **kwargs)

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


admin.site.register(Teammate)
