# Generated by Django 2.2.10 on 2020-03-29 02:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0025_auto_20200328_0342'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='covidcases',
            name='death',
        ),
        migrations.RemoveField(
            model_name='covidcases',
            name='tested_negative',
        ),
        migrations.RemoveField(
            model_name='covidcases',
            name='tested_positive',
        ),
        migrations.RemoveField(
            model_name='covidcases',
            name='total_tested',
        ),
        migrations.AddField(
            model_name='covidcases',
            name='age',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='covidcases',
            name='came_from',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='covidcases',
            name='current_status',
            field=models.CharField(default='unknown', max_length=31),
        ),
        migrations.AddField(
            model_name='covidcases',
            name='detected_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='covidcases',
            name='district_id',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='cases', to='api.District'),
        ),
        migrations.AddField(
            model_name='covidcases',
            name='gender',
            field=models.CharField(default='Male', max_length=15),
        ),
        migrations.AddField(
            model_name='covidcases',
            name='in_isolation',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='covidcases',
            name='labrotary',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='covidcases',
            name='municipality_id',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='cases', to='api.Municipality'),
        ),
        migrations.AddField(
            model_name='covidcases',
            name='province_id',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='cases', to='api.Province'),
        ),
        migrations.AddField(
            model_name='covidcases',
            name='remarks',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='covidcases',
            name='returned_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='covidcases',
            name='transit',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
