# Generated by Django 3.2.7 on 2021-09-18 12:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0015_comment_datetime'),
    ]

    operations = [
        migrations.AlterField(
            model_name='listing',
            name='photo',
            field=models.CharField(blank=True, default=None, max_length=1000),
        ),
    ]
