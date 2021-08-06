from django.contrib import admin

from .forms import PlayerInlineAdminForm
from .models import Game, PlayerStat, Teammate

DEFAULT_PLAYERS = ["Jejy", "AliceCheshir", "Leutik", "Helizen", "Renn_Kane"]
DEFAULT_POKEMONS = ["ZERAORA", "LUCARIO", "PIKACHU", "CRAMORANT", "SNORLAX"]


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


admin.site.register(Teammate)
