# Generated by Django 3.0.1 on 2020-07-13 15:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ITYW', '0003_auto_20200713_1325'),
    ]

    operations = [
        migrations.CreateModel(
            name='itemstock',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('item_kind', models.CharField(max_length=20)),
                ('item_stock_num', models.IntegerField(blank=True, null=True)),
            ],
        ),
    ]