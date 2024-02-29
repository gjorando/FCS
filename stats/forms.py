from django import forms

from stats.models import PlayerStat, Game, Season


class PokemonChoiceIterator(forms.models.ModelChoiceIterator):
    """
    The choice iterator for PokemonChoiceField that actually orders them by category.
    """

    def __iter__(self):
        groups = {}  # We fully iterate our raw list of Pokémon to create categories
        for item in super().__iter__():
            if isinstance(item[0], forms.models.ModelChoiceIteratorValue):
                category = item[0].instance.get_category_display()
                if category in groups:
                    groups[category].append(item[0].instance)
                else:
                    groups[category] = [item[0].instance]
            else:
                yield item

        # Then we yield each group, sorted by name
        for group, objs in sorted(groups.items(), key=lambda x: x[0]):
            objs = sorted(objs, key=lambda x: x.name)
            yield group, [self.choice(obj) for obj in objs]


class PokemonChoiceField(forms.ModelChoiceField):
    """
    A custom choice field that orders Pokémon by category.
    """

    def __init__(self, *args, **kwargs):
        self.iterator = PokemonChoiceIterator

        super().__init__(*args, **kwargs)

    def label_from_instance(self, obj):
        return obj.name


class GamesListFilterForm(forms.Form):
    """
    Form for the games list page.
    """

    per_page = forms.IntegerField(label="Éléments par page", label_suffix="", min_value=1, initial=10, required=False)
    season = forms.IntegerField(label="Saison", label_suffix="", min_value=1, initial=None, required=False)

    def clean_per_page(self):
        return self.cleaned_data["per_page"] or 10

    def clean_season(self):
        return self.cleaned_data["season"] or None


def formfield_for_game_model(db_field, **kwargs):
    """
    Customize some fields of the Game admin form.
    """

    # Seasons
    if db_field.name == "season":
        return forms.ModelChoiceField(queryset=Season.objects.all())
    return db_field.formfield(**kwargs)


class GameAdminForm(forms.ModelForm):
    """
    Custom model form for the games.
    """

    class Meta:
        model = Game
        exclude = tuple()
        formfield_callback = formfield_for_game_model


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
    """
    Form for the prefill admin view.
    """

    picture = forms.FileField(label="Écran de résultat")
