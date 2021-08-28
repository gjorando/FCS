from django import forms

from stats.models import PlayerStat, Game


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

        super(PlayerInlineAdminForm, self).__init__(*args, **kwargs)

        if player_id < 0:
            return

        instance = getattr(self, 'instance', None)
        if instance:
            # Cannot change the is_opponent field
            self.fields["is_opponent"].disabled = True


class PrefillForm(forms.Form):
    picture = forms.FileField(label="Écran de résultat")
