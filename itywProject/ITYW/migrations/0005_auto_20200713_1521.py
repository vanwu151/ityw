# Generated by Django 3.0.1 on 2020-07-13 15:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ITYW', '0004_itemstock'),
    ]

    operations = [
        migrations.AddField(
            model_name='itemchangeinfo',
            name='item_statu',
            field=models.CharField(default='', max_length=2),
        ),
        migrations.AddField(
            model_name='iteminfo',
            name='item_statu',
            field=models.CharField(default='', max_length=2),
        ),
    ]
