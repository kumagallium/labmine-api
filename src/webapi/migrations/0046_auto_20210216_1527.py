# Generated by Django 2.2.1 on 2021-02-16 06:27

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('webapi', '0045_auto_20210202_1302'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Process',
            new_name='Node',
        ),
        migrations.RenameField(
            model_name='default',
            old_name='process',
            new_name='node',
        ),
        migrations.RenameField(
            model_name='entity',
            old_name='process',
            new_name='node',
        ),
        migrations.RenameField(
            model_name='figure',
            old_name='process',
            new_name='node',
        ),
        migrations.RenameField(
            model_name='node',
            old_name='process_name',
            new_name='node_name',
        ),
    ]
