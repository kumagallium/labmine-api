# Generated by Django 2.2.1 on 2021-02-16 08:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('webapi', '0049_auto_20210216_1715'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='metadata',
            name='metakey',
        ),
        migrations.AddField(
            model_name='metadata',
            name='item',
            field=models.ForeignKey(default='', on_delete=django.db.models.deletion.PROTECT, to='webapi.Item'),
            preserve_default=False,
        ),
    ]
