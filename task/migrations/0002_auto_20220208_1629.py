# Generated by Django 2.2.9 on 2022-02-08 08:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('task', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='pcName',
        ),
        migrations.AddField(
            model_name='user',
            name='bindIp',
            field=models.CharField(default=11, max_length=30, verbose_name='绑定IP'),
            preserve_default=False,
        ),
    ]