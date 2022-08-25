# Generated by Django 2.2.9 on 2022-02-16 09:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('task', '0002_auto_20220214_0858'),
    ]

    operations = [
        migrations.CreateModel(
            name='Percent',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=15, verbose_name='描述')),
                ('ident', models.CharField(max_length=10, verbose_name='标识')),
                ('percent', models.FloatField(max_length=3, verbose_name='百分比')),
            ],
            options={
                'verbose_name': '百分比',
                'verbose_name_plural': '百分比',
            },
        ),
    ]
