# Generated by Django 2.2.10 on 2020-03-25 06:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0017_auto_20200325_0427'),
    ]

    operations = [
        migrations.AddField(
            model_name='provincedata',
            name='hotline',
            field=models.TextField(default=''),
            preserve_default=False,
        ),
    ]