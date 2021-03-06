import pymysql
import paramiko
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from task.models import Record


class MyDB:
    def __init__(self, **dbinfo):
        self.dbinfo = dbinfo

    def connect(self):
        conn = pymysql.connect(
            # 传入一个字典
            **self.dbinfo
        )
        return conn


class MySSH:
    def __init__(self, **sshinfo):
        self.sshinfo = sshinfo

    def connect(self):
        conn = paramiko.SSHClient()
        conn.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        conn.connect(**self.sshinfo)

        return conn


class GetFile:
    def __init__(self, **sevinfo):
        self.sevinfo = sevinfo

    def connect(self):
        trans = paramiko.Transport(sock=(self.sevinfo['hostname'], self.sevinfo['port']))
        trans.connect(username=self.sevinfo['username'], password=self.sevinfo['password'])
        sftp = paramiko.SFTPClient.from_transport(trans)

        return sftp


class OptRecord:
    def __init__(self, request):
        self.request = request
        try:
            self.remote_ip = self.request.META['REMOTE_ADDR']
            self.path = self.request.path
        except:
            self.remote_ip = 'zhangsan'
            self.path = '/'

    def opt_record(self):
        re_ip = Record.objects.filter(remoteIp=self.remote_ip, path=self.path)

        if re_ip:
            re_ip[0].count += 1
            re_ip[0].save()
        else:
            Record.objects.create(remoteIp=self.remote_ip, count=1, path=self.path)


def page_infos(data, count, page):
    paginator = Paginator(data, count)
    try:
        info = paginator.page(page)
    except PageNotAnInteger:
        info = paginator.page(1)
    except EmptyPage:
        info = paginator.page(paginator.num_pages)

    return info
