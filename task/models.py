from django.db import models


# Create your models here.
class Type(models.Model):
    id = models.AutoField('ID', primary_key=True)
    name = models.CharField('任务类型', max_length=10, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '任务类型'
        verbose_name_plural = '任务类型'


class Hours(models.Model):
    id = models.AutoField('ID', primary_key=True)
    month = models.CharField('月份', max_length=6, unique=True)
    workDay = models.FloatField('工作日', max_length=3)
    dayHours = models.FloatField('日工时（h）', max_length=2)
    state = models.CharField('状态', max_length=2, default=1)

    def __str__(self):
        return self.month

    class Meta:
        verbose_name = '每月工时配置'
        verbose_name_plural = '每月工时配置'


class User(models.Model):
    id = models.AutoField('ID', primary_key=True)
    name = models.CharField('名字', max_length=10, unique=True)
    pinyin = models.CharField('拼音名', max_length=20)
    bindIp = models.CharField('绑定IP', max_length=30)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '测试人员'
        verbose_name_plural = '测试人员'


class Status(models.Model):
    id = models.AutoField('ID', primary_key=True)
    name = models.CharField('状态名', max_length=10, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '任务状态'
        verbose_name_plural = '任务状态'


class Task(models.Model):
    id = models.AutoField('ID', primary_key=True)
    date = models.ForeignKey(Hours, on_delete=models.CASCADE, verbose_name='月份')
    type = models.ForeignKey(Type, on_delete=models.CASCADE, verbose_name='任务类型')
    item = models.CharField('需求编号', max_length=15)
    name = models.CharField('描述', max_length=50)
    hours = models.FloatField('工时（h）', max_length=5)
    tester = models.CharField('测试负责人', max_length=10, blank=True)
    status = models.ForeignKey(Status, on_delete=models.CASCADE, verbose_name='状态')
    delay = models.IntegerField('延期', choices=((0, '是'), (1, '否'), (2, '即将')), default=1)
    start = models.DateField('开始时间')
    end = models.DateField('截止时间')
    updated = models.DateField('更新时间', auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '任务管理'
        verbose_name_plural = '任务管理'


class Record(models.Model):
    id = models.AutoField('ID', primary_key=True)
    remoteIp = models.CharField('访问IP', max_length=30)
    count = models.IntegerField('访问次数', default=0)
    path = models.CharField('访问地址', max_length=30)
    created = models.DateTimeField('创建时间', auto_now_add=True)
    updated = models.DateTimeField('更新时间', auto_now=True)

    def __str__(self):
        return self.remoteIp

    class Meta:
        verbose_name = '操作记录'
        verbose_name_plural = '操作记录'


class Percent(models.Model):
    id = models.AutoField('ID', primary_key=True)
    name = models.CharField('描述', max_length=15)
    ident = models.CharField('标识', max_length=10)
    percent = models.FloatField('百分比', max_length=3)
    score = models.IntegerField('分数', default=0)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '百分比'
        verbose_name_plural = '百分比'


class Score(models.Model):
    id = models.AutoField('ID', primary_key=True)
    type = models.CharField('类型', choices=(('H', '工时'), ('B', 'BUG')), default='H', max_length=5)
    month = models.ForeignKey(Hours, on_delete=models.CASCADE, verbose_name='月份')
    tester = models.CharField('姓名', max_length=5)
    score = models.IntegerField('分数', default=0)
    desc = models.CharField('描述', max_length=50, blank=True)

    def __str__(self):
        return self.tester

    class Meta:
        verbose_name = '个人积分'
        verbose_name_plural = '个人积分'
