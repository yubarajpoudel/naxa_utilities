# Generated by Django 2.2.10 on 2020-03-24 12:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0011_auto_20200324_1213'),
    ]

    operations = [
        migrations.AddField(
            model_name='provincedata',
            name='active',
            field=models.BooleanField(default=True),
        ),
    ]