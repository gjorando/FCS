from django import forms

from stats.models import PlayerStat, Game

DEFAULT_PLAYERS = ["Jejy", "AliceCheshir", "Leutik", "Helizen", "Renn_Kane"]
DEFAULT_POKEMONS = ["ZERAORA", "LUCARIO", "PIKACHU", "CRAMORANT", "SNORLAX"]


class PokemonChoiceIterator(forms.models.ModelChoiceIterator):
    def __iter__(self):
        groups = {}
        for item in super().__iter__():
            if isinstance(item[0], forms.models.ModelChoiceIteratorValue):
                category = item[0].instance.get_category_display()
                if category in groups:
                    groups[category].append(item[0].instance)
                else:
                    groups[category] = [item[0].instance]
            else:
                yield item

        for group, objs in sorted(groups.items(), key=lambda x: x[0]):
            objs = sorted(objs, key=lambda x: x.name)
            yield group, [self.choice(obj) for obj in objs]


class PokemonChoiceField(forms.ModelChoiceField):
    def __init__(self, *args, **kwargs):
        self.iterator = PokemonChoiceIterator

        super().__init__(*args, **kwargs)

    def label_from_instance(self, obj):
        return obj.name


class GamesListFilterForm(forms.Form):
    per_page = forms.IntegerField(label="Éléments par page", label_suffix="", min_value=1, initial=10, required=False)
    season = forms.IntegerField(label="Saison", label_suffix="", min_value=1, initial=None, required=False)

    def clean_per_page(self):
        return self.cleaned_data["per_page"] or 10

    def clean_season(self):
        return self.cleaned_data["season"] or None


class GameAdminForm(forms.ModelForm):
    """
    Custom model form for the games.
    """

    class Meta:
        model = Game
        exclude = tuple()


class PlayerInlineAdminForm(forms.ModelForm):
    """
    Custom model form for the players in a game.
    """

    class Meta:
        model = PlayerStat
        exclude = tuple()

    def __init__(self, *args, **kwargs):
        try:
            player_id = kwargs["prefix"].split("-")[1]
        except KeyError:
            player_id = -1
        try:
            player_id = int(player_id)  # Entries for each player
        except ValueError:
            player_id = -1  # Other entries (which are skipped and not shown)

        if (not ("instance" in kwargs and kwargs["instance"])) and ("initial" not in kwargs):
            initial_values = {
                "scored": 0,
                "kills": 0,
                "assists": 0,
                "result": 10
            }

            if player_id < 0:  # We skip these entries
                pass
            elif player_id < 5:  # The 5 first entries are the ally team
                # Pre-set the names of each player as well as their default Pokémon
                initial_values["pseudo"] = DEFAULT_PLAYERS[player_id]
                initial_values["pokemon"] = DEFAULT_POKEMONS[player_id]
            else:  # The 5 last are the opposing team
                initial_values["is_opponent"] = True

            kwargs["initial"] = initial_values

        super(PlayerInlineAdminForm, self).__init__(*args, **kwargs)

        if player_id < 0:
            return

        instance = getattr(self, 'instance', None)
        if instance:
            # Cannot change the is_opponent field as well as the ally pseudos
            self.fields["is_opponent"].disabled = True
            if player_id < 5:
                self.fields["pseudo"].disabled = True


class PrefillForm(forms.Form):
    picture = forms.FileField(label="Écran de résultat")
