# Generated by Django 4.2.5 on 2023-10-28 17:39

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("main", "0010_remove_user_is_timed_out_thread_is_locked"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="bio",
            field=models.TextField(
                default="Clique no lapis para escrever uma bio", null=True
            ),
        ),
        migrations.AlterField(
            model_name="user",
            name="avatar",
            field=models.ImageField(
                default="avatars/default.webp", upload_to="avatars"
            ),
        ),
    ]
