# Generated by Django 2.2.9 on 2022-03-02 06:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('task', '0004_auto_20220223_0906'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='delay',
            field=models.IntegerField(choices=[(0, '是'), (1, '否'), (2, '即将')], default=1, verbose_name='延期'),
        ),
    ]
