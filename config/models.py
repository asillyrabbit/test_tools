from django.db import models


class EnvInfo(models.Model):
    id = models.AutoField('序号', primary_key=True)
    name = models.CharField('名称', max_length=30, unique=True)
    info = models.TextField('环境信息', max_length=300)
    ident = models.CharField('唯一标识', max_length=20)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '环境信息'
        verbose_name_plural = '环境信息'


class ComInfo(models.Model):
    id = models.AutoField('序号', primary_key=True)
    name = models.CharField('命令名称', max_length=30, unique=True)
    command = models.CharField('执行命令', max_length=100)
    ident = models.CharField('唯一标识', max_length=20)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '命令信息'
        verbose_name_plural = '命令信息'
