# Generated by Django 3.2.5 on 2021-08-13 13:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('stats', 'populate_pokemon'),
    ]

    operations = [
        migrations.AlterField(
            model_name='playerstat',
            name='pokemon',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='stats.pokemon'),
        ),
    ]
