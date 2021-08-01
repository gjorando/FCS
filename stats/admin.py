from django.contrib import admin
from django import forms

from .models import Game, PlayerStat

DEFAULT_PLAYERS = ["Jejy", "AliceCheshir", "Leutik", "Helizen", "Renn_Kane"]
DEFAULT_POKEMONS = ["ZERAORA", "LUCARIO", "PIKACHU", "CRAMORANT", "SNORLAX"]

class PlayerInlineForm(forms.ModelForm):
    """
    Custom model form for the players in a game.
    """

    class Meta:
        model = PlayerStat
        fields = ("pseudo", "pokemon", "is_opponent", "scored", "kills",
                  "assists", "result")

    def __init__(self, *args, **kwargs):
        try:
            player_id = kwargs["prefix"].split("-")[1]
        except KeyError:
            player_id = -1
        try:
            player_id = int(player_id)  # Entries for each player
        except ValueError:
            player_id = -1  # Other entries (which are skipped and not shown)

        initial_values = {}

        if player_id < 0:  # We skip these entries
            pass
        elif player_id < 5:  # The 5 first entries are the ally team
            # Pre-set the names of each player as well as their default Pokémon
            initial_values["pseudo"] = DEFAULT_PLAYERS[player_id]
            initial_values["pokemon"] = DEFAULT_POKEMONS[player_id]
        else:  # The 5 last are the opposing team
            initial_values["is_opponent"] = True

        kwargs["initial"] = initial_values

        super(PlayerInlineForm, self).__init__(*args, **kwargs)

        if player_id < 0:
            return

        instance = getattr(self, 'instance', None)
        if instance:
            # Cannot change the is_opponent field as well as the ally pseudos
            self.fields["is_opponent"].disabled = True
            if player_id < 5:
                self.fields["pseudo"].disabled = True

class PlayerInline(admin.TabularInline):
    """
    Displays exactly ten players when creating a game.
    """

    model = PlayerStat
    form = PlayerInlineForm
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
    list_filter = ["season", "is_won"]
