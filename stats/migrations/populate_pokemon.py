from django.db import migrations

LIST_POKEMONS = [
    ("A", (
        ("GARDEVOIR", "Gardevoir"),
        ("PIKACHU", "Pikachu"),
        ("GRENINJA", "Greninja"),
        ("VENUSAUR", "Venusaur"),
        ("A_NINETALES", "Alolan Ninetales"),
        ("CRAMORANT", "Cramorant"),
        ("CINDERACE", "Cinderace"),
    )),
    ("S", (
        ("ZERAORA", "Zeraora"),
        ("TALONFLAME", "Talonflame"),
        ("ABSOL", "Absol"),
        ("GENGAR", "Gengar"),
    )),
    ("AR", (
        ("CHARIZARD", "Charizard"),
        ("LUCARIO", "Lucario"),
        ("MACHAMP", "Machamp"),
        ("GARCHOMP", "Garchomp"),
    )),
    ("D", (
        ("SNORLAX", "Snorlax"),
        ("CRUSTLE", "Crustle"),
        ("SLOWBRO", "Slowbro"),
    )),
    ("S", (
        ("ELDEGOSS", "Eldegoss"),
        ("MR_MIME", "Mr. Mime"),
        ("WIGGLYTUFF", "Wigglytuff"),
    ))
]


def populate_pokemon(apps, schema_editor):
    """
    Populate with the existing pokémons.
    """

    Pokemon = apps.get_model("stats", "Pokemon")
    for category, pokemons in LIST_POKEMONS:
        for id_p, name in pokemons:
            Pokemon.objects.create(
                id=id_p,
                name=name,
                category=category
            ).save()


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ('stats', '0004_pokemon'),
    ]

    operations = [
        migrations.RunPython(populate_pokemon)
    ]
