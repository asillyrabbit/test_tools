from django.shortcuts import render, redirect
from test_tools.common import MyDB, MySSH, GetFile, OptRecord
from config.models import EnvInfo, ComInfo
from django.http import HttpResponse, FileResponse, JsonResponse
import time
import os
import json

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
test_report_name = '知了v1.2.0-测试日报.xlsx'


# Create your views here.
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

    stp_doc = ComInfo.objects.get(ident='stp_doc').command
    stp_pat = ComInfo.objects.get(ident='stp_pat').command
    stp_back = ComInfo.objects.get(ident='stp_back').command

    server_info = eval(EnvInfo.objects.get(ident='TestServer').info)

    myssh = MySSH(**server_info)
    conn = myssh.connect()

    ident = requests.GET['ident']

    if ident == 'up_testing':
        results = exe_commd(ident, conn, up_testing)
    if ident == 're_doc':
        exe_commd(ident, conn, stp_doc)
        # 暂停3秒，等待所有进程停止
        time.sleep(3)
        results = exe_commd(ident, conn, re_doc)
    if ident == 're_pat':
        exe_commd(ident, conn, stp_pat)
        time.sleep(3)
        results = exe_commd(ident, conn, re_pat)
    if ident == 're_back':
        exe_commd(ident, conn, stp_back)
        time.sleep(3)
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

    # get_pty=True解决stdout中没有数据或有一行没有输出时导致执行卡住的情况
    stdin, stdout, stderr = conn.exec_command(commd, get_pty=True)
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


# 2021-12-2新增
def qmodule(requests):
    callback = requests.GET['callback']
    term = requests.GET['term']

    # 执行命令集
    server_info = eval(EnvInfo.objects.get(ident='chandao').info)
    remote_dir = "/opt/qbugs/"
    query_commd = f"python3 {remote_dir}qmodule.py {term}"

    # 链接服务器
    myssh = MySSH(**server_info)
    conn = myssh.connect()

    # 执行重命名、统计操作
    stdin, stdout, stderr = conn.exec_command(query_commd)
    names = stdout.read().decode()
    names = eval(names)
    names = list(names.values())

    m_name = f"{callback}({names})"

    return HttpResponse(m_name)


def newbugs(requests):
    if requests.method != 'POST':
        return render(requests, 'operate/newbugs.html')
    else:
        mname = requests.POST['mname']

    # 执行命令集
    server_info = eval(EnvInfo.objects.get(ident='chandao').info)
    remote_dir = "/opt/qbugs/"
    query_commd = f"python3 {remote_dir}qbugs.py {mname}"

    # 链接服务器
    myssh = MySSH(**server_info)
    conn = myssh.connect()

    stdin, stdout, stderr = conn.exec_command(query_commd)
    bugs = stdout.read().decode()
    bugs = eval(bugs)
    bugs_len = len(bugs)

    totals, opened, type_dict, level_dict, n_list, t_list, o_list = data_format(bugs)

    name_list, to_list, op_list = dict_sort(n_list, t_list, o_list)

    type_data, type_name = format_dict(type_dict)
    level_data, level_name = format_dict(level_dict)

    context = {'bugs': bugs, 'totals': totals, 'opened': opened, 'type_dict': type_dict, 'level_dict': level_dict,
               'name_list': name_list, 'to_list': to_list, 'op_list': op_list, 'type_data': type_data,
               'type_name': type_name, 'level_data': level_data, 'level_name': level_name, 'bugs_len': bugs_len}

    return render(requests, 'operate/newbugs.html', context)


def data_format(data):
    totals, opened = 0, 0
    function, practice, load, compatibility, ui, demand, security = 0, 0, 0, 0, 0, 0, 0
    level2, level3, level4, level5 = 0, 0, 0, 0
    type_dict, level_dict = {}, {}
    name_list, to_list, op_list = [], [], []

    for k, v in data.items():
        to = v['total']
        op = v['opened']
        if v['total'] > 0:
            name_list.append(k)
            to_list.append(to)
            op_list.append(op)

            totals += to
            opened += op

            v['type'].setdefault('功能', 0)
            v['type'].setdefault('用户体验', 0)
            v['type'].setdefault('性能', 0)
            v['type'].setdefault('兼容', 0)
            v['type'].setdefault('UI', 0)
            v['type'].setdefault('需求', 0)
            v['type'].setdefault('安全性', 0)
            v['level'].setdefault('严重', 0)
            v['level'].setdefault('一般', 0)
            v['level'].setdefault('提示', 0)
            v['level'].setdefault('建议', 0)

            function += v['type']['功能']
            practice += v['type']['用户体验']
            load += v['type']['性能']
            compatibility += v['type']['兼容']
            ui += v['type']['UI']
            demand += v['type']['需求']
            security += v['type']['安全性']
            level2 += v['level']['严重']
            level3 += v['level']['一般']
            level4 += v['level']['提示']
            level5 += v['level']['建议']

    type_dict['功能'] = function
    type_dict['用户体验'] = practice
    type_dict['性能'] = load
    type_dict['兼容'] = compatibility
    type_dict['UI'] = ui
    type_dict['需求'] = demand
    type_dict['安全性'] = security

    level_dict['严重'] = level2
    level_dict['一般'] = level3
    level_dict['提示'] = level4
    level_dict['建议'] = level5

    return totals, opened, type_dict, level_dict, name_list, to_list, op_list


def dict_sort(name_list, to_list, op_list):
    dict1 = dict(zip(name_list, to_list))
    dict2 = dict(zip(name_list, op_list))

    temp = sorted(dict1.items(), key=lambda kv: (kv[1], kv[0]))

    n_list = []
    t_list = []
    o_list = []

    for name, count in temp:
        n_list.append(name)
        t_list.append(count)
        t = dict2[name]
        o_list.append(t)

    return n_list, t_list, o_list


def format_dict(target_dict):
    pie_data = []
    pie_name = []
    for k, v in target_dict.items():
        if v > 0:
            t_dict = {'value': v, 'name': k}
            pie_data.append(t_dict)
            pie_name.append(k)

    return pie_data, pie_name


# 2022-01-19新增检查处方药品供应商功能
def checkpres(requests):
    if requests.method != 'POST':
        return render(requests, 'operate/checkpres.html')
    else:
        orderno = requests.POST['orderno']

        dbinfo = eval(EnvInfo.objects.get(ident='TestDB').info)

        sup_t = "gyy_supplier_t"
        pre_med_t = "gyy_prescription_medical_t"
        sup_med_t = "gyy_suplier_medical_t"
        pre_pat_med_t = "gyy_prescription_patent_medical_t"
        sup_pat_med_t = "gyy_suplier_patent_medical_t"
        order_t = "gyy_order_t"

        q_med_pres = f"select d.id,d.shot_name,a.id,a.name from {sup_med_t} a,{sup_t} d where a.id in" \
                     f" (select b.s_m_id from {pre_med_t} b where b.prescripiton_id in (select c.relation_id " \
                     f"from {order_t} c where c.order_no='{orderno}')) and a.supplier=d.id;"

        q_med_supp = f"select d.name from {sup_med_t} a,{sup_t} d where a.id in (select b.s_m_id from {pre_med_t} " \
                     f"b where b.prescripiton_id in (select c.relation_id from {order_t} c where " \
                     f"c.order_no='{orderno}')) and a.supplier=d.id group by a.supplier;"

        q_pat_pres = f"select d.id,d.shot_name,a.id,a.name from {sup_pat_med_t} a,gyy_supplier_t d where a.id in " \
                     f"(select b.s_m_id from {pre_pat_med_t} b where b.prescripiton_id in (select c.relation_id " \
                     f"from {order_t} c where c.order_no='{orderno}')) and a.supplier=d.id;"

        q_pat_supp = f"select d.name from {sup_pat_med_t} a,gyy_supplier_t d where a.id in (select b.s_m_id from " \
                     f"{pre_pat_med_t} b where b.prescripiton_id in (select c.relation_id from {order_t} c where " \
                     f"c.order_no='{orderno}')) and a.supplier=d.id group by a.supplier;"

        q_med = f"select a.name,b.name as sup_med_t,c.name as pre_med_t from {sup_med_t} a," \
                f"{sup_t} b,(select c1.s_m_id,c2.name from {pre_med_t} c1,{sup_t} c2 " \
                f"where c1.supplier=c2.id and c1.prescripiton_id in(select relation_id from {order_t} where " \
                f"order_no='{orderno}' and stype='0')) as c where a.id=c.s_m_id and a.supplier=b.id"

        q_pat = f"select a.name,b.name as sup_med_t,c.name as pre_med_t from {sup_pat_med_t} a," \
                f"{sup_t} b,(select c1.s_m_id,c2.name from {pre_pat_med_t} c1," \
                f"{sup_t} c2 where c1.supplier=c2.id and c1.prescripiton_id in(select relation_id from " \
                f"{order_t} where order_no='{orderno}' and stype='0')) as c where a.id=c.s_m_id and a.supplier=b.id"

        mydb = MyDB(**dbinfo)
        con = mydb.connect()
        cur = con.cursor()

        cur.execute(q_med)
        com_sups = cur.fetchall()

        p_type = 'med'
        if not com_sups:
            cur.execute(q_pat)
            com_sups = cur.fetchall()
            p_type = 'pat'

        comparison = 0
        for com_sup in com_sups:
            if com_sup[1] != com_sup[2]:
                comparison = 1
                break

        if comparison == 1:
            context = {'com_sups': com_sups, 'comparison': comparison}
        else:
            if p_type == 'med':
                cur.execute(q_med_pres)
                pres_infos = cur.fetchall()
                cur.execute(q_med_supp)
                supp_infos = cur.fetchall()
            else:
                cur.execute(q_pat_pres)
                pres_infos = cur.fetchall()
                cur.execute(q_pat_supp)
                supp_infos = cur.fetchall()

            supp_num = len(supp_infos)
            supp_str = ''
            for supp in supp_infos:
                supp_str = supp_str + supp[0] + '、'

            supp_str = supp_str.strip('、')

            context = {'pres_infos': pres_infos, 'supp_num': supp_num, 'supp_str': supp_str, 'comparison': comparison}

        cur.close()
        con.close()

        return render(requests, 'operate/checkpres.html', context)
