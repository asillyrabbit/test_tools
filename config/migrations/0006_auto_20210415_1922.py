# Generated by Django 2.2.9 on 2021-04-15 11:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('config', '0005_auto_20210415_1920'),
    ]

    operations = [
        migrations.AlterField(
            model_name='envinfo',
            name='envinfo',
            field=models.TextField(max_length=300, verbose_name='环境信息'),
        ),
    ]
