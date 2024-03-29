# Generated by Django 2.2.9 on 2022-02-09 08:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Hours',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID')),
                ('month', models.CharField(max_length=6, unique=True, verbose_name='月份')),
                ('workDay', models.FloatField(max_length=3, verbose_name='工作日')),
                ('dayHours', models.FloatField(max_length=2, verbose_name='日工时（h）')),
                ('state', models.CharField(default=1, max_length=2, verbose_name='状态')),
            ],
            options={
                'verbose_name': '每月工时配置',
                'verbose_name_plural': '每月工时配置',
            },
        ),
        migrations.CreateModel(
            name='Record',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID')),
                ('remoteIp', models.CharField(max_length=30, verbose_name='访问IP')),
                ('count', models.IntegerField(default=0, verbose_name='访问次数')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('updated', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
            ],
            options={
                'verbose_name': '操作记录',
                'verbose_name_plural': '操作记录',
            },
        ),
        migrations.CreateModel(
            name='Status',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=10, unique=True, verbose_name='状态名')),
            ],
            options={
                'verbose_name': '任务状态',
                'verbose_name_plural': '任务状态',
            },
        ),
        migrations.CreateModel(
            name='Type',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=10, unique=True, verbose_name='任务类型')),
            ],
            options={
                'verbose_name': '任务类型',
                'verbose_name_plural': '任务类型',
            },
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=10, unique=True, verbose_name='名字')),
                ('bindIp', models.CharField(max_length=30, verbose_name='绑定IP')),
            ],
            options={
                'verbose_name': '测试人员',
                'verbose_name_plural': '测试人员',
            },
        ),
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID')),
                ('item', models.CharField(max_length=15, verbose_name='需求编号')),
                ('name', models.CharField(max_length=50, verbose_name='描述')),
                ('hours', models.FloatField(max_length=5, verbose_name='工时（h）')),
                ('tester', models.CharField(blank=True, max_length=10, verbose_name='测试负责人')),
                ('start', models.DateField(verbose_name='开始时间')),
                ('end', models.DateField(verbose_name='截止时间')),
                ('date', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='task.Hours', verbose_name='月份')),
                ('status', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='task.Status', verbose_name='状态')),
                ('type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='task.Type', verbose_name='任务类型')),
            ],
            options={
                'verbose_name': '任务管理',
                'verbose_name_plural': '任务管理',
            },
        ),
    ]
