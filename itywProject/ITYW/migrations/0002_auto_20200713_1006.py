# Generated by Django 3.0.1 on 2020-07-13 10:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ITYW', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='hardwareinfo',
            name='hardware_location',
            field=models.CharField(default='', max_length=50),
        ),
        migrations.AddField(
            model_name='itemchangeinfo',
            name='item_change_location',
            field=models.CharField(default='', max_length=50),
        ),
    ]
