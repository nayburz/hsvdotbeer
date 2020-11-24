# Generated by Django 3.1.2 on 2020-11-15 14:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("tap_list_providers", "0003_auto_20200602_2202"),
    ]

    operations = [
        migrations.AlterField(
            model_name="apiratelimittimestamp",
            name="api_type",
            field=models.CharField(
                choices=[
                    ("untappd", "Untappd"),
                    ("digitalpour", "DigitalPour"),
                    ("taphunter", "TapHunter"),
                    ("manual", "Chalkboard/Whiteboard"),
                    ("", "Unknown"),
                    ("test", "TEST LOCAL PROVIDER"),
                    ("stemandstein", "The Stem & Stein's HTML"),
                    ("taplist.io", "taplist.io"),
                    ("beermenus", "BeerMenus"),
                    ("arryved_embedded_menu", "Arryved Embedded Menu"),
                ],
                max_length=50,
                unique=True,
            ),
        ),
    ]