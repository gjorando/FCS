from django.db import migrations


def restore_speedsters(apps, schema_editor):
    """
    Fixes a development blunder, where speedsters had the same category id as supports.
    """

    Pokemon = apps.get_model("stats", "Pokemon")
    Pokemon.objects.filter(id__in=["ZERAORA", "TALONFLAME", "ABSOL", "GENGAR"]).update(category="SS")


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ('stats', '0001_alter_pokemon_category'),
    ]

    operations = [
        migrations.RunPython(restore_speedsters)
    ]
