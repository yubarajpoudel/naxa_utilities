# Generated by Django 2.2.10 on 2020-04-16 11:05

import django.contrib.gis.db.models.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0057_auto_20200416_1034'),
    ]

    operations = [
        migrations.AddField(
            model_name='municipality',
            name='geom',
            field=django.contrib.gis.db.models.fields.MultiPolygonField(blank=True, null=True, srid=4326),
        ),
        migrations.AddField(
            model_name='news',
            name='category',
            field=models.CharField(choices=[('News', 'News'), ('Press Release', 'Press Release'), ('Situation Report', 'Situation Report')], default='News', max_length=255),
        ),
    ]
