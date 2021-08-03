from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator

LIST_POKEMONS = [
    ("Attacker", (
        ("GARDEVOIR", "Gardevoir"),
        ("PIKACHU", "Pikachu"),
        ("GRENINJA", "Greninja"),
        ("VENUSAUR", "Venusaur"),
        ("A_NINETALES", "Alolan Ninetales"),
        ("CRAMORANT", "Cramorant"),
        ("CINDERACE", "Cinderace"),
    )),
    ("Speedster", (
        ("ZERAORA", "Zeraora"),
        ("TALONFLAME", "Talonflame"),
        ("ABSOL", "Absol"),
        ("GENGAR", "Gengar"),
    )),
    ("All-rounder", (
        ("CHARIZARD", "Charizard"),
        ("LUCARIO", "Lucario"),
        ("MACHAMP", "Machamp"),
        ("GARCHOMP", "Garchomp"),
    )),
    ("Defender", (
        ("SNORLAX", "Snorlax"),
        ("CRUSTLE", "Crustle"),
        ("SLOWBRO", "Slowbro"),
    )),
    ("Supporter", (
        ("ELDEGOSS", "Eldegoss"),
        ("MR_MIME", "Mr. Mime"),
        ("WIGGLYTUFF", "Wigglytuff"),
    ))
]


class Game(models.Model):
    """
    Stores the results of a game as well as the individual results of each
    player.
    """

    class Meta:
        verbose_name = "Partie"

    date = models.DateTimeField("Date du match")
    season = models.PositiveIntegerField("Saison", validators=[MinValueValidator(1)])
    is_won = models.BooleanField("Partie gagnée", default=False)
    score_allies = models.PositiveIntegerField("Score allié")
    score_opponents = models.PositiveIntegerField("Score opposants")

    def __str__(self):
        return "Partie du {} ({})".format(
            self.date.strftime("%d/%m/%Y à %H:%M"),
            "gagnée" if self.is_won else "perdue"
        )


def restrict_amount(value):
    """
    Validates the number of players in a game.

    :param value: Game id.
    """
    # FIXME count exactly 5 players per team instead of maximum number for whole game
    # Maybe use a constraint instead?
    if PlayerStat.objects.filter(game=value).count() >= 10:
        raise ValidationError("La partie à déjà 10 joueurs.")


class PlayerStat(models.Model):
    """
    Stores the results of a player for a given game.
    """

    class Meta:
        verbose_name = "Joueur"
        constraints = [
            models.UniqueConstraint(fields=["game", "pseudo"], name="no_duplicate_players"),
            models.UniqueConstraint(fields=["game", "pokemon", "is_opponent"], name="no_duplicate_pokemons_in_team")
        ]

    game = models.ForeignKey(Game, on_delete=models.CASCADE, validators=[restrict_amount,])
    pseudo = models.CharField("Pseudo", max_length=64)
    pokemon = models.CharField("Pokémon joué", max_length=64, choices=LIST_POKEMONS)
    is_opponent = models.BooleanField("Joueur adverse")
    scored = models.PositiveIntegerField("Points marqués")
    kills = models.PositiveIntegerField("Nombre de KOs")
    assists = models.PositiveIntegerField("Nombre d'assists")
    result = models.PositiveIntegerField("Note globale")

    def __str__(self):
        return "{}: {}({}) S{}/K{}/A{}/{}".format(
            "Adversaire" if self.is_opponent else "FCS",
            self.pseudo,
            self.get_pokemon_display(),
            self.scored,
            self.kills,
            self.assists,
            self.result
        )

    def clean(self):
        # If a player is an ally, check that it exists in the Teammate model
        if not self.is_opponent:
            if len(Teammate.objects.filter(pseudo=self.pseudo)) == 0:
                raise ValidationError("{}: ce coéquipier n'existe pas.".format(self.pseudo))


class Teammate(models.Model):
    """
    Lists the players of the team that is tracked by the app.
    """

    class Meta:
        verbose_name = "Coéquipier"

    pseudo = models.CharField("Pseudo", max_length=64, primary_key=True)

    def __str__(self):
        return self.pseudo