from datetime import datetime

from django.db import migrations, models

def update_time(apps, schema_editor):
    """
    Fills the new_date DateTime field with the date from the old date Date
    field.
    """

    Game = apps.get_model("stats", "Game")
    for game in Game.objects.all():
        game.new_date = datetime.combine(game.date, datetime.min.time())
        game.save()

class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ('stats', '0001_initial'),
    ]

    operations = [
        migrations.AddField(  # Add the new DateTime field w/ a temporary name
            model_name='game',
            name='new_date',
            field=models.DateTimeField(default="2000-01-01", verbose_name='Date du match'),
            preserve_default=False,
        ),
        migrations.RunPython(update_time),  # Fills the new field
        migrations.RemoveField(  # Remove the old field
            model_name='game',
            name='date',
        ),
        migrations.RenameField(  # Rename the new field
            model_name='game',
            old_name='new_date',
            new_name='date',
        ),
    ]
