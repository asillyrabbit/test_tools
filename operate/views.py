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
        if userinfo[4] == 5:
            userinfo[4] = '广盛康'

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

    dbinfo = eval(EnvInfo.objects.get(ident='TestDB').info)
    mydb = MyDB(**dbinfo)
    con = mydb.connect()
    cur = con.cursor()

    if apptype == '患者':
        command = f"{clear_pat} {userid} {openid} 1"
    if apptype == '医生':
        command = f"{clear_doc} {userid} {openid} {scan}"
    if apptype == '泰康用户':
        command = f"{clear_pat} {userid} {openid} 3"
    if apptype == '广盛康':
        command = f"{clear_pat} {userid} {openid} 5"
        up_sql = f"update gyy_cooperation_user_t set mobile={mobile}+100000000,name='作废卡' where mobile='{mobile}'"
        cur.execute(up_sql)
        con.commit()

    myssh = MySSH(**server_info)
    conn = myssh.connect()
    stdin, stdout, stderr = conn.exec_command(command)
    out = stdout.read()
    conn.close()

    # 验证清理结果
    query_info = f"select mobile from gyy_user_t where id={userid}"
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

    if ident == 'up_testing':
        results = exe_commd(ident, conn, up_testing)
    if ident == 're_doc':
        results = exe_commd(ident, conn, re_doc)
    if ident == 're_pat':
        results = exe_commd(ident, conn, re_pat)
    if ident == 're_back':
        results = exe_commd(ident, conn, re_back)

    conn.close()

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

        flag = 0

        if doc_infos is None:
            flag = 1

        context = {'doc_infos': doc_infos, 'flag': flag}

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


def oplat(requests):
    verify_data = ComInfo.objects.get(ident='verify_data')
    auto_verify = ComInfo.objects.get(ident='auto_verify')
    s_t_msg = ComInfo.objects.get(ident='s_t_msg')
    st_withdraw = ComInfo.objects.get(ident='st_withdraw')

    com_infos = []
    com_infos.append(verify_data)
    com_infos.append(auto_verify)
    com_infos.append(s_t_msg)
    com_infos.append(st_withdraw)

    context = {'com_infos': com_infos}

    if requests.method != 'POST':
        return render(requests, 'operate/oplat.html', context)
    else:
        mobile = requests.POST['mobile']
        query_sql = f"select name,mobile,openid from gyy_sales_t where mobile='{mobile}' limit 1"

        dbinfo = eval(EnvInfo.objects.get(ident='TestDB').info)
        mydb = MyDB(**dbinfo)
        con = mydb.connect()
        cur = con.cursor()
        cur.execute(query_sql)
        sale_info = cur.fetchone()
        con.close()

        flag = 1
        if sale_info is None:
            flag = 0

        context = {'sale_info': sale_info, 'flag': flag, 'com_infos': com_infos}

        return render(requests, 'operate/oplat.html', context)


def platopt(requests):
    name = requests.GET['sname'] + '_del'
    mobile = requests.GET['smobile']
    openid = requests.GET['sopenid']

    new_mobile = int(mobile) + 1000000000

    update_sql = f"update gyy_sales_t set name='{name}',mobile='{new_mobile}',openid='' where mobile='{mobile}'"

    dbinfo = eval(EnvInfo.objects.get(ident='TestDB').info)
    mydb = MyDB(**dbinfo)
    con = mydb.connect()
    cur = con.cursor()
    cur.execute(update_sql)
    con.commit()
    con.close()

    if openid != '':
        del_redis = ComInfo.objects.get(ident='del_redis').command
        del_redis = del_redis.replace('keywords', f'ggy::s::sale::openid::{openid}')

        server_info = eval(EnvInfo.objects.get(ident='TestServer').info)
        myssh = MySSH(**server_info)
        conn = myssh.connect()
        stdin, stdout, stderr = conn.exec_command(del_redis)
        conn.close()

    status = '<p class="text-success">成功</p>'
    clear_msg = '<div class ="alert alert-success"><strong>操作成功！</strong><br/>请退出微信，重新登录。</div>'

    results = {
        'status': status,
        'clear_msg': clear_msg
    }

    return JsonResponse(results)


def querysales(requests):
    callback = requests.GET['callback']
    term = requests.GET['term']

    dbinfo = eval(EnvInfo.objects.get(ident='TestDB').info)
    mydb = MyDB(**dbinfo)
    con = mydb.connect()
    cur = con.cursor()

    date_now = time.strftime("%Y%m", time.localtime())

    query_infos = f"select id,name from gyy_sales_t where id in(select sale_id from gyy_sales_month_account_t where account_month='{date_now}') and openid !='' and name like'%{term}%'order by id;"

    cur.execute(query_infos)
    sales_infos = cur.fetchall()

    sales_name_id = []
    for sales_info in sales_infos:
        sales_name_id.append(f"{sales_info[1]}({sales_info[0]})")

    con.close()

    salse = f"{callback}({sales_name_id})"

    return HttpResponse(salse)


def modmonth(requests):
    name = requests.GET['salename']
    sale_id = str(name).split('(')[1].strip(')')

    year = int(time.strftime("%Y", time.localtime()))
    month = int(time.strftime("%m", time.localtime()))

    now_month = time.strftime("%Y%m", time.localtime())

    if month == 1:
        year -= 1
        month = 12
    else:
        if month > 10:
            month -= 1
        else:
            month -= 1
            month = f"0{month}"

    pre_month = f"{year}{month}"

    update_1 = f"update gyy_sales_month_account_t set account_month = '{pre_month}' where sale_id='{sale_id}' and account_month='{now_month}';"
    update_2 = f"update gyy_sales_account_log_t set account_month = '{pre_month}' where sale_id='{sale_id}' and account_month='{now_month}';"

    dbinfo = eval(EnvInfo.objects.get(ident='TestDB').info)
    mydb = MyDB(**dbinfo)
    con = mydb.connect()
    cur = con.cursor()

    cur.execute(update_1)
    cur.execute(update_2)
    con.commit()
    con.close()

    succ_msg = f"<div class =\"alert alert-success\"><strong>操作成功！</strong><br/>账期已由{now_month}调整为{pre_month}，下一步可以进行销售结算操作。</div>"

    return HttpResponse(succ_msg)


def postatus(requests):
    verify_data = ComInfo.objects.get(ident='verify_data').command
    auto_verify = ComInfo.objects.get(ident='auto_verify').command
    st_withdraw = ComInfo.objects.get(ident='st_withdraw').command
    s_t_msg = ComInfo.objects.get(ident='s_t_msg').command

    server_info = eval(EnvInfo.objects.get(ident='TestServer').info)

    myssh = MySSH(**server_info)
    conn = myssh.connect()

    ident = requests.GET['ident']

    if ident == 'verify_data':
        results = exe_commd(ident, conn, verify_data)
    if ident == 'auto_verify':
        results = exe_commd(ident, conn, auto_verify)
    if ident == 'st_withdraw':
        results = exe_commd(ident, conn, st_withdraw)
    if ident == 's_t_msg':
        results = exe_commd(ident, conn, s_t_msg)

    conn.close()

    return JsonResponse(results)


# 执行服务器命令公共方法
def exe_commd(ident, conn, commd):
    succ = "<a href='#succmsg'>成功</a>"
    fail = "<a href='#errmsg'>失败</a>"

    results = {
        'result': '',
        'succ_msg': '',
        'fail_msg': ''
    }

    stdin, stdout, stderr = conn.exec_command(commd)
    logs = stdout.read().decode()
    logs = logs.replace('\n', '<br/>').lstrip('b\'').rstrip('\'')
    if len(logs) == 0:
        logs = '没有日志输出！'
    if ('error' in logs) or ('Error' in logs):
        results['result'] = fail
        results['fail_msg'] = f"<div class=\"alert alert-danger\"><p>{logs}</p></div>"
    else:
        results['result'] = succ
        results['succ_msg'] = f"<div class=\"alert alert-success\"><p>{logs}</p></div>"

    return results
