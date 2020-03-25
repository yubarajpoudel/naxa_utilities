# Generated by Django 2.2.10 on 2020-03-25 06:54

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0018_provincedata_hotline'),
    ]

    operations = [
        migrations.CreateModel(
            name='AgeGroupData',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('hlcit_code', models.CharField(max_length=63)),
                ('pcode', models.CharField(max_length=31)),
                ('l0_14', models.IntegerField(default=0)),
                ('l15_49', models.IntegerField(default=0)),
                ('l50plus', models.IntegerField(default=0)),
                ('ltotal', models.IntegerField(default=0)),
                ('district', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='age', to='api.District')),
                ('municipality', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='age', to='api.Municipality')),
            ],
        ),
    ]
