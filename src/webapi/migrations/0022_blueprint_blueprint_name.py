# Generated by Django 2.2.1 on 2020-04-21 06:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webapi', '0021_auto_20200421_1437'),
    ]

    operations = [
        migrations.AddField(
            model_name='blueprint',
            name='blueprint_name',
            field=models.CharField(default='', max_length=255),
            preserve_default=False,
        ),
    ]
