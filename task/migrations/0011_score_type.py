# Generated by Django 2.2.9 on 2022-02-21 07:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('task', '0010_record_path'),
    ]

    operations = [
        migrations.AddField(
            model_name='score',
            name='type',
            field=models.CharField(choices=[('H', '工时'), ('B', 'BUG')], default='H', max_length=5, verbose_name='类型'),
        ),
    ]