# Generated by Django 2.2.10 on 2020-04-01 06:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0035_auto_20200401_0506'),
    ]

    operations = [
        migrations.CreateModel(
            name='DeviceMessage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(choices=[('message', 'Message'), ('url', 'Url'), ('page', 'Page')], default='message', max_length=15)),
                ('title', models.CharField(blank=True, max_length=255, null=True)),
                ('message', models.CharField(blank=True, max_length=255, null=True)),
                ('url', models.CharField(blank=True, max_length=255, null=True)),
            ],
        ),
    ]