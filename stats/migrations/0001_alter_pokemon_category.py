# Generated by Django 3.2.5 on 2021-09-13 14:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stats', 'pokemon_blissey'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pokemon',
            name='category',
            field=models.CharField(choices=[('AR', 'All-rounder'), ('A', 'Attacker'), ('D', 'Defender'), ('SS', 'Speedster'), ('S', 'Supporter')], max_length=5, verbose_name='Catégorie'),
        ),
    ]
