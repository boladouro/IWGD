# Generated by Django 4.2.5 on 2023-10-25 21:27

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("main", "0006_alter_post_thread_alter_post_user_alter_thread_user_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="reports",
            name="action",
            field=models.TextField(default=None, null=True),
        ),
        migrations.AlterField(
            model_name="reports",
            name="mod_reason",
            field=models.TextField(default=None, null=True),
        ),
    ]
