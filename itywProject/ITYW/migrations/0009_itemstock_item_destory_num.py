# Generated by Django 3.0.1 on 2020-07-16 14:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ITYW', '0008_itemstock_item_stock_location'),
    ]

    operations = [
        migrations.AddField(
            model_name='itemstock',
            name='item_destory_num',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
