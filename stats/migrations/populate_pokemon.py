from datetime import datetime

from django.db import migrations, models

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


def update_time(apps, schema_editor):
    """
    Fills the new_date DateTime field with the date from the old date Date
    field.
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
        migrations.RunPython(update_time)
    ]
