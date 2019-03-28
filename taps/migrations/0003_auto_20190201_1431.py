# Generated by Django 2.1.3 on 2019-02-01 14:31

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('taps', '0002_tap_beer'),
    ]

    operations = [
        migrations.AddField(
            model_name='tap',
            name='time_added',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AddField(
            model_name='tap',
            name='time_updated',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]