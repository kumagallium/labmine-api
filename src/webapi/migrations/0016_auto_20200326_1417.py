# Generated by Django 2.2.1 on 2020-03-26 05:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webapi', '0015_auto_20200326_0955'),
    ]

    operations = [
        migrations.AlterField(
            model_name='property',
            name='property_name',
            field=models.CharField(default='', max_length=255),
        ),
        migrations.AlterField(
            model_name='unit',
            name='symbol',
            field=models.CharField(default='', max_length=255),
        ),
    ]
