# Generated by Django 2.2.10 on 2020-03-23 05:47

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0008_auto_20200323_0544'),
    ]

    operations = [
        migrations.AlterField(
            model_name='provincedata',
            name='province_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='Province', to='api.Province'),
        ),
    ]
