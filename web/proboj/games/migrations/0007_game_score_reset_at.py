# Generated by Django 4.2.7 on 2023-11-30 08:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("games", "0006_game_bot_timeout"),
    ]

    operations = [
        migrations.AddField(
            model_name="game",
            name="score_reset_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
