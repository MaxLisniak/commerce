# Generated by Django 3.2.7 on 2021-09-12 15:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0008_user_watchlist'),
    ]

    operations = [
        migrations.AddField(
            model_name='listing',
            name='active',
            field=models.BooleanField(default=True),
        ),
    ]