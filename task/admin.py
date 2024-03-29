from django.contrib import admin
from .models import Type, User, Status, Task, Hours, Record, Percent, Score


# Register your models here.

@admin.register(Type)
class ConfigsAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']
    search_fields = ['name']
    ordering = ['id']


@admin.register(User)
class ConfigsAdmin(admin.ModelAdmin):
    list_display = ['id', 'pinyin', 'name', 'bindIp']
    search_fields = ['name']
    ordering = ['id']


@admin.register(Status)
class ConfigsAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']
    search_fields = ['name']
    ordering = ['id']


@admin.register(Task)
class ConfigsAdmin(admin.ModelAdmin):
    list_display = ['id', 'date', 'type', 'app', 'item', 'name', 'hours', 'tester', 'status', 'delay', 'start', 'end',
                    'updated']
    search_fields = ['tester']
    ordering = ['-id']
    list_per_page = 15


@admin.register(Hours)
class ConfigsAdmin(admin.ModelAdmin):
    list_display = ['id', 'month', 'workDay', 'dayHours', 'state']
    search_fields = ['month']
    ordering = ['id']


@admin.register(Record)
class ConfigsAdmin(admin.ModelAdmin):
    list_display = ['id', 'remoteIp', 'path', 'count', 'created', 'updated']
    search_fields = ['pcName']
    ordering = ['-updated']


@admin.register(Percent)
class ConfigsAdmin(admin.ModelAdmin):
    list_display = ['id', 'ident', 'name', 'percent', 'score']
    search_fields = ['name']
    ordering = ['id']


@admin.register(Score)
class ConfigsAdmin(admin.ModelAdmin):
    list_display = ['id', 'type', 'month', 'tester', 'score', 'desc']
    search_fields = ['tester']
    ordering = ['id']
