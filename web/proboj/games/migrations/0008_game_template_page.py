# Generated by Django 4.2.7 on 2023-12-21 13:41

import django.db.models.deletion
from django.db import migrations, models

import proboj.games.models
import proboj.storage


class Migration(migrations.Migration):

    dependencies = [
        ("games", "0007_game_score_reset_at"),
    ]

    operations = [
        migrations.AddField(
            model_name="game",
            name="template",
            field=models.FileField(
                blank=True,
                storage=proboj.storage.OverwriteStorage(),
                upload_to=proboj.games.models._game_template,
            ),
        ),
        migrations.CreateModel(
            name="Page",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=128)),
                ("slug", models.SlugField(max_length=128)),
                ("content", models.TextField(blank=True)),
                (
                    "game",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="games.game"
                    ),
                ),
            ],
            options={
                "ordering": ["game", "name"],
            },
        ),
    ]
