# Generated by Django 2.2.10 on 2020-04-02 14:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0043_auto_20200402_0821'),
    ]

    operations = [
        migrations.AddField(
            model_name='userreport',
            name='result',
            field=models.CharField(default='lesslikely', max_length=255),
        ),
    ]
