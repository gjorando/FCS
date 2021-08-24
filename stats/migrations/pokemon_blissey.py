from django.db import migrations


def add_pokemon(apps, schema_editor):
    """
    Adds Blissey to the pokémon list, if it doesn't exist already.
    """

    Pokemon = apps.get_model("stats", "Pokemon")
    try:
        obj = Pokemon.objects.get(id="BLISSEY")
        print("Blissey already exists, skipping creation.")
    except Pokemon.DoesNotExist:
        obj = Pokemon(
            id="BLISSEY",
            name="Blissey",
            category="S"
        )
        obj.save()


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ('stats', '0001_alter_playerstat_pokemon'),
    ]

    operations = [
        migrations.RunPython(add_pokemon)
    ]
