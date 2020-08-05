# Generated by Django 3.0.1 on 2020-07-10 16:36

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='admininfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('admin_name', models.CharField(max_length=20)),
                ('admin_password', models.CharField(default='', max_length=128)),
            ],
        ),
        migrations.CreateModel(
            name='hardwareinfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('hardware_name', models.CharField(max_length=20)),
                ('hardware_kind', models.CharField(max_length=20)),
                ('hardware_sn', models.CharField(max_length=50)),
                ('hardware_now_user', models.CharField(max_length=50)),
                ('hardware_info', models.CharField(max_length=500)),
            ],
        ),
        migrations.CreateModel(
            name='itemchangeinfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('item_change_date', models.DateTimeField(default=django.utils.timezone.now, verbose_name='更新时间')),
                ('item_name', models.CharField(max_length=50)),
                ('item_sn', models.CharField(max_length=50)),
                ('item_pass_user', models.CharField(max_length=20)),
                ('item_now_user', models.CharField(max_length=20)),
                ('item_change_info', models.CharField(max_length=500)),
            ],
        ),
        migrations.CreateModel(
            name='useritemsinfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_name', models.CharField(max_length=50)),
                ('user_pc_sn', models.CharField(max_length=50)),
                ('user_notebook_sn', models.CharField(max_length=50)),
                ('user_phone_sn', models.CharField(max_length=50)),
                ('user_pad_sn', models.CharField(max_length=50)),
                ('user_phone_num', models.CharField(max_length=50)),
                ('user_wechat_name', models.CharField(max_length=50)),
                ('user_qianniu_name', models.CharField(max_length=50)),
                ('user_otheritems', models.CharField(max_length=500)),
            ],
        ),
    ]