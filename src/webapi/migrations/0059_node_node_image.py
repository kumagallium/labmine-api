# Generated by Django 2.2.1 on 2021-03-10 02:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webapi', '0058_auto_20210305_0906'),
    ]

    operations = [
        migrations.AddField(
            model_name='node',
            name='node_image',
            field=models.ImageField(default='images/node_default.png', upload_to='images/'),
        ),
    ]
