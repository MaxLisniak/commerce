# Generated by Django 3.2.7 on 2021-09-12 18:37

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0012_alter_listing_datetime'),
    ]

    operations = [
        migrations.AlterField(
            model_name='listing',
            name='datetime',
            field=models.DateTimeField(default=datetime.datetime(2021, 9, 12, 18, 37, 30, 430087)),
        ),
    ]
