# Generated by Django 3.2.5 on 2021-08-01 18:05

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('stats', 'game_datetime'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Player',
            new_name='PlayerStat',
        ),
    ]