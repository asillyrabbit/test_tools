# Generated by Django 2.2.9 on 2021-04-15 11:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('config', '0006_auto_20210415_1922'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cominfo',
            name='remark',
        ),
        migrations.RemoveField(
            model_name='envinfo',
            name='remark',
        ),
    ]