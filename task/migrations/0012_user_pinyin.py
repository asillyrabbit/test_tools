# Generated by Django 2.2.9 on 2022-02-23 07:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('task', '0011_score_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='pinyin',
            field=models.CharField(default=11, max_length=20, verbose_name='拼音名'),
            preserve_default=False,
        ),
    ]
