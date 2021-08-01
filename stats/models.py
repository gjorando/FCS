from django.db import models
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
    score_allies = models.PositiveIntegerField("Score allié", validators=[MinValueValidator(1)])
    score_opponents = models.PositiveIntegerField("Score opposants", validators=[MinValueValidator(1)])

    def __str__(self):
        return "Partie du {} ({})".format(
            self.date.strftime("%d/%m/%Y à %H:%M"),
            "gagnée" if self.is_won else "perdue"
        )


class PlayerStat(models.Model):
    """
    Stores the results of a player for a given game.
    """

    class Meta:
        verbose_name = "Joueur"

    game = models.ForeignKey(Game, on_delete=models.CASCADE)
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
