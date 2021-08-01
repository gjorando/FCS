from django import forms

class GamesListFilterForm(forms.Form):
    per_page = forms.IntegerField(label="Éléments par page", label_suffix="", min_value=1, initial=10, required=False)
    season = forms.IntegerField(label="Saison", label_suffix="", min_value=1, initial=None, required=False)

    def clean_per_page(self):
        return self.cleaned_data["per_page"] or 10

    def clean_season(self):
        return self.cleaned_data["season"] or None
