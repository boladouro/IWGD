# Generated by Django 4.2.5 on 2023-10-22 16:54

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("main", "0004_alter_thread_latest_update"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="favorites",
            field=models.ManyToManyField(related_name="favorites", to="main.topico"),
        ),
    ]