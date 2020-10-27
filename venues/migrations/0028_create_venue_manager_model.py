# Generated by Django 3.0.8 on 2020-10-15 15:21

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("beers", "0034_auto_20200602_2202"),
        ("venues", "0027_auto_20200124_2059"),
    ]

    operations = [
        migrations.CreateModel(
            name="VenueTapManager",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "default_manufacturer",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="default_managers",
                        to="beers.Manufacturer",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="venue_tap_managers",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "venue",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="venue_tap_managers",
                        to="venues.Venue",
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="venue",
            name="managers",
            field=models.ManyToManyField(
                related_name="venues_managed",
                through="venues.VenueTapManager",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddConstraint(
            model_name="venuetapmanager",
            constraint=models.UniqueConstraint(
                fields=("user", "venue"), name="user-venue-unique"
            ),
        ),
    ]