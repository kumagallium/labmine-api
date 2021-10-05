# Generated by Django 2.2.1 on 2021-02-16 08:20

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('webapi', '0050_auto_20210216_1717'),
    ]

    operations = [
        migrations.CreateModel(
            name='Explanation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('figure', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='webapi.Figure')),
                ('headline', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='webapi.Headline')),
            ],
        ),
    ]
