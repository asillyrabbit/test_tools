from django.contrib import admin

from .models import EnvInfo, ComInfo

admin.site.site_title = '测试工具平台后台管理系统'
admin.site.site_header = '测试工具平台'


# Register your models here.


@admin.register(EnvInfo)
class ConfigsAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'info', 'ident']
    search_fields = ['name']
    ordering = ['id']


@admin.register(ComInfo)
class ComInfoAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'command', 'ident']
    search_fields = ['name']
    ordering = ['id']
