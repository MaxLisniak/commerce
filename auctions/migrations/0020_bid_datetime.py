# Generated by Django 3.2.7 on 2021-09-19 09:04

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0019_notification'),
    ]

    operations = [
        migrations.AddField(
            model_name='bid',
            name='datetime',
            field=models.DateTimeField(default=datetime.datetime(2021, 9, 12, 0, 0)),
        ),
    ]
