# Generated by Django 4.2.6 on 2024-01-13 11:04

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("carshop", "0010_monosettings"),
    ]

    operations = [
        migrations.AlterField(
            model_name="monosettings",
            name="public_key",
            field=models.CharField(max_length=250, unique=True),
        ),
    ]
