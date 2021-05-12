from django.shortcuts import render, redirect
from test_tools.common import MyDB, MySSH, GetFile
from config.models import EnvInfo, ComInfo
from django.http import HttpResponse, FileResponse, JsonResponse
import time
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
test_report_name = '知了v1.2.0-测试日报.xlsx'


# Create your views here.
def search(request):
    if request.method != 'POST':
        return render(request, 'operate/search.html')
    else:
        mobile = request.POST['mobile']

    query_info = f"SELECT a.id,a.mobile,a.nickname,b.third_account,b.apptype,b.created " \
                 f"FROM gyy_user_t a,gyy_user_third_t b where a.id=b.userid and a.mobile={mobile}"

    dbinfo = eval(EnvInfo.objects.get(ident='TestDB').info)
    mydb = MyDB(**dbinfo)
    con = mydb.connect()
    cur = con.cursor()
    cur.execute(query_info)
    uinfos = cur.fetchall()
    con.close()

    userinfos = []

    for uinfo in uinfos:
        userinfos.append(list(uinfo))

    for userinfo in userinfos:
        if userinfo[4] == 1:
            userinfo[4] = '患者'
        if userinfo[4] == 2:
            userinfo[4] = '医生'
        if userinfo[4] == 3:
            userinfo[4] = '泰康用户'

        userinfo[5] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(userinfo[5]))

    userinfos.sort(key=lambda elem: elem[5], reverse=True)
    list_len = len(userinfos)

    context = {'userinfos': userinfos, 'list_len': list_len}

    return render(request, 'operate/clear.html', context)


def clear(request):
    userid = request.POST['userid']
    mobile = request.POST['mobile']
    openid = request.POST['openid']
    apptype = request.POST['apptype']
    scan = request.POST['scan']

    if scan == '清':
        scan = 1
    else:
        scan = 0

    server_info = eval(EnvInfo.objects.get(ident='TestServer').info)
    clear_doc = ComInfo.objects.get(ident='doc').command
    clear_pat = ComInfo.objects.get(ident='pat').command

    if apptype == '患者':
        command = f"{clear_pat} {userid} {openid} 1"
    if apptype == '医生':
        command = f"{clear_doc} {userid} {openid} {scan}"
    if apptype == '泰康用户':
        command = f"{clear_pat} {userid} {openid} 3"

    myssh = MySSH(**server_info)
    conn = myssh.connect()
    stdin, stdout, stderr = conn.exec_command(command)
    out = stdout.read()
    conn.close()

    query_info = f"select mobile from gyy_user_t where id={userid}"
    dbinfo = eval(EnvInfo.objects.get(ident='TestDB').info)
    mydb = MyDB(**dbinfo)
    con = mydb.connect()
    cur = con.cursor()
    cur.execute(query_info)
    new_mobile = cur.fetchall()[0][0]
    con.close()

    if mobile == new_mobile:
        msg = '操作失败，请重试或手动清理！'
    else:
        msg = '操作成功，请重新登录微信！'

    context = {'msg': msg}
    return render(request, 'operate/success.html', context)


def bugs(requests):
    if requests.method != 'POST':
        return render(requests, 'operate/bugs.html')
    else:
        mname = requests.POST['mname']

    # 执行命令集
    server_info = eval(EnvInfo.objects.get(ident='chandao').info)
    remote_dir = ComInfo.objects.get(ident='getBugs').command

    rename_commd = f"python3 {remote_dir}rename.py {mname}"
    static_commd = f"python3 {remote_dir}run.py"
    clear_commd = f"python3 {remote_dir}clear.py"

    # 链接服务器
    myssh = MySSH(**server_info)
    conn = myssh.connect()

    # 执行重命名、统计操作
    stdin, stdout, stderr = conn.exec_command(rename_commd)
    stdin, stdout, stderr = conn.exec_command(static_commd)

    # 链接SFTP，下载文件
    file_found = 1
    file_dir = os.path.join(BASE_DIR, 'static', 'file')

    getfile = GetFile(**server_info)
    sftp = getfile.connect()
    sftp.chdir(remote_dir)
    try:
        # 下载时会先创建一个空文件，如果之前文件存在，会被覆盖
        sftp.get(f"{remote_dir}{test_report_name}", f"{file_dir}/{test_report_name}")
        stdin, stdout, stderr = conn.exec_command(clear_commd)
    except FileNotFoundError as e:
        file_found = 0
    finally:
        sftp.close()
        conn.close()

    context = {'mname': mname, 'file_found': file_found, 'test_report_name': test_report_name}
    return render(requests, 'operate/bugs.html', context)


def download(requests):
    file_dir = os.path.join(BASE_DIR, 'static', 'file')
    os.chdir(file_dir)
    file = open(test_report_name, 'rb')
    response = FileResponse(file)
    response['Content-Type'] = 'application/octet-stream'
    response['Content-Disposition'] = 'attachment;filename="{}"'.format(test_report_name).encode('utf-8', 'ISO-8859-1')
    return response


def update(requests):
    up_testing = ComInfo.objects.get(ident='up_testing')
    re_doc = ComInfo.objects.get(ident='re_doc')
    re_pat = ComInfo.objects.get(ident='re_pat')
    re_back = ComInfo.objects.get(ident='re_back')

    com_infos = []
    com_infos.append(up_testing)
    com_infos.append(re_doc)
    com_infos.append(re_pat)
    com_infos.append(re_back)

    context = {'com_infos': com_infos}

    return render(requests, 'operate/update.html', context)


def state(requests):
    up_testing = ComInfo.objects.get(ident='up_testing').command
    re_doc = ComInfo.objects.get(ident='re_doc').command
    re_pat = ComInfo.objects.get(ident='re_pat').command
    re_back = ComInfo.objects.get(ident='re_back').command

    server_info = eval(EnvInfo.objects.get(ident='TestServer').info)

    myssh = MySSH(**server_info)
    conn = myssh.connect()

    ident = requests.GET['ident']

    succ = "<a href='#succmsg' onclick=\"document.getElementById('succmsg').style.display=''\">成功</a>"
    fail = "<a href='#errmsg' onclick=\"document.getElementById('errmsg').style.display=''\">失败</a>"

    results = {
        'result': '成功',
        'msg': '',
    }

    if ident == 'up_testing':
        stdin, stdout, stderr = conn.exec_command(up_testing)
        logs = stdout.read().decode()
        logs = logs.replace('\n', '<br/>').lstrip('b\'').rstrip('\'')
        if 'error' in logs:
            results['result'] = fail
            results['msg'] = logs
        else:
            results['result'] = succ
            results['msg'] = logs

    if ident == 're_doc':
        stdin, stdout, stderr = conn.exec_command(re_doc)
    if ident == 're_pat':
        stdin, stdout, stderr = conn.exec_command(re_pat)
    if ident == 're_back':
        stdin, stdout, stderr = conn.exec_command(re_back)

    return JsonResponse(results)


def qrcode(requests):
    if requests.method != 'POST':
        return render(requests, 'operate/qrcode.html')
    else:
        mobile = requests.POST['mobile']

        dbinfo = eval(EnvInfo.objects.get(ident='TestDB').info)

        query_info = f"select userid,name,mobile,hospital FROM gyy_doctor_t where mobile='{mobile}' and status='4' limit 1"

        mydb = MyDB(**dbinfo)
        con = mydb.connect()
        cur = con.cursor()
        cur.execute(query_info)
        doc_infos = cur.fetchone()
        cur.close()

        doc_infos_len = len(doc_infos)

        context = {'doc_infos': doc_infos, 'doc_infos_len': doc_infos_len}

        return render(requests, 'operate/qrcode.html', context)


def recode(requests):
    otype = requests.GET['otype']
    userid = requests.GET['userid']

    dbinfo = eval(EnvInfo.objects.get(ident='TestDB').info)
    mydb = MyDB(**dbinfo)
    con = mydb.connect()
    cur = con.cursor()

    if otype == '医生二维码':
        up_sql = f"update gyy_doctor_t set my_qrcode='',qrcode_token='' where userid='{userid}'"
        cur.execute(up_sql)

    if otype == '医拉医二维码':
        up_sql = f"update gyy_doctor_t set sale_qrcode='',sale_token='' where userid='{userid}'"
        cur.execute(up_sql)

    con.commit()
    con.close()

    server_info = eval(EnvInfo.objects.get(ident='TestServer').info)
    del_redis = ComInfo.objects.get(ident='del_redis').command
    del_redis = del_redis.replace('keywords', f'ggy::s::doctor::{userid}')

    myssh = MySSH(**server_info)
    conn = myssh.connect()
    stdin, stdout, stderr = conn.exec_command(del_redis)

    if otype == '医拉医二维码':
        create_code = f"php /data/web/testing/backend/yii /msg/invitation-qrcode {userid}"
        stdin, stdout, stderr = conn.exec_command(del_redis)
    conn.close()

    result = '<div class ="alert alert-success"><strong>操作成功！</strong><br/>请重新登录应用（微信或APP），查看最新二维码。</div>'

    return HttpResponse(result)
