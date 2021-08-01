import django.core.validators
from django.db import migrations, models

def set_scores(apps, schema_editor):
    """
    Tries to deduce the score of a match based on the individual points scored by each member. As some extra points can
    granted by the game (ex: with Rotom), it may yield values that differ from the actual result.
    """

    Game = apps.get_model("stats", "Game")
    for game in Game.objects.all():
        score_allies = 0
        score_opponents = 0
        player_stats = game.playerstat_set.all()
        for stat in player_stats:
            if stat.is_opponent:
                score_opponents += stat.scored
            else:
                score_allies += stat.scored

        game.score_allies = score_allies
        game.score_opponents = score_opponents
        game.save()

class Migration(migrations.Migration):

    dependencies = [
        ('stats', '0001_rename_player_playerstat'),
    ]

    operations = [
        migrations.AddField(
            model_name='game',
            name='score_allies',
            field=models.PositiveIntegerField(default=0, validators=[django.core.validators.MinValueValidator(1)], verbose_name='Score allié'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='game',
            name='score_opponents',
            field=models.PositiveIntegerField(default=0, validators=[django.core.validators.MinValueValidator(1)], verbose_name='Score opposants'),
            preserve_default=False,
        ),
        migrations.RunPython(set_scores),
    ]
