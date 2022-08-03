import time

from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.
from config.models import EnvInfo, ComInfo
from test_tools.common import MyDB, MySSH, OptRecord


def clear(request):
    re = OptRecord(request)
    re.opt_record()

    url = 'clear:clear'

    if request.method != "POST":
        context = {'url': url}
        return render(request, 'clear/clear.html', context)
    else:
        mobile = request.POST['mobile']

    dbinfo = eval(EnvInfo.objects.get(ident='TestDB').info)
    mydb = MyDB(**dbinfo)
    con = mydb.connect()
    cur = con.cursor()

    q_all = f"select a.id,a.mobile,a.nickname,b.third_account,b.apptype,b.created " \
            f"from gyy_user_t a,gyy_user_third_t b where a.id=b.userid and a.mobile={mobile}"

    is_exist = f"{q_all} and b.apptype='2'"

    q_doc = f"select userid,mobile,name,'无（APP注册用户）' as openid,2 as app_type,created " \
            f"from gyy_doctor_t where mobile={mobile} order by updated desc limit 1"

    q_sales = f"select id,mobile,name,openid,'销售' as apptype,created from gyy_sales_t where " \
              f"mobile='{mobile}' limit 1"

    cur.execute(is_exist)
    doc_exist = cur.fetchall()
    cur.execute(q_all)
    u_infos = cur.fetchall()
    cur.execute(q_doc)
    doc_info = cur.fetchone()
    cur.execute(q_sales)
    sale_info = cur.fetchone()

    user_infos = []

    if len(doc_exist) == 0 and doc_info is not None:
        user_infos.append(list(doc_info))

    for u_info in u_infos:
        user_infos.append(list(u_info))

    if sale_info is not None:
        user_infos.append(list(sale_info))

    print(user_infos)

    for user_info in user_infos:
        if user_info[4] == 1:
            user_info[4] = '患者'
        elif user_info[4] == 2:
            user_info[4] = '医生'
        elif user_info[4] == 3:
            user_info[4] = '泰康用户'
        elif user_info[4] == 5:
            user_info[4] = '广盛康'
        elif user_info[4] == '销售':
            pass
        else:
            app_id = user_info[4]
            q_app_name = f'select app_name from gyy_td_part_info where id={app_id}'
            cur.execute(q_app_name)
            app_name = cur.fetchone()[0]
            user_info[4] = app_name
        user_info[5] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(user_info[5]))

        if user_info[3].endswith('_bak'):
            user_info.append(1)
        else:
            user_info.append(0)

    cur.close()
    con.close()

    user_infos.sort(key=lambda elem: elem[4], reverse=False)
    info_len = len(user_infos)

    context = {'user_infos': user_infos, 'url': url, 'info_len': info_len}

    return render(request, 'clear/clear.html', context)


def update(requests):
    utype = requests.GET['utype']
    userid = requests.GET['userid']
    mobile = requests.GET['mobile']
    openid = requests.GET['openid']

    dbinfo = eval(EnvInfo.objects.get(ident='TestDB').info)
    mydb = MyDB(**dbinfo)
    con = mydb.connect()
    cur = con.cursor()

    command = ''
    server_info = eval(EnvInfo.objects.get(ident='TestServer').info)
    myssh = MySSH(**server_info)
    conn = myssh.connect()

    app_type = 0
    if utype == '销售':
        new_mobile = int(mobile) + 1000000000
        name = requests.GET['name']
        up_sql = f"update gyy_sales_t set name='{name}_del',mobile='{new_mobile}',openid='{openid}_del' where id={userid}"
        cur.execute(up_sql)
        con.commit()
        com_command = ComInfo.objects.get(ident='del_redis').command
        # command在下面公共代码执行
        command = com_command.replace('keywords', f'ggy::s::sale::openid::{openid}')
        command1 = com_command.replace('keywords', f'ggy::s::sale::saleid::{userid}')
        stdin, stdout, stderr = conn.exec_command(command1)
        out = stdout.read()
    else:
        scan = requests.GET['scan']
        if scan == '清理':
            scan = 1
        else:
            scan = 0

        clear_doc = ComInfo.objects.get(ident='doc').command
        clear_pat = ComInfo.objects.get(ident='pat').command
        clear_patplus = ComInfo.objects.get(ident='PatPlus').command
        q_us_count = f"select count(userid) from gyy_user_third_t where userid={userid} and third_account not like'%_bak'"
        cur.execute(q_us_count)
        us_count = cur.fetchone()[0]

        if utype == '患者':
            if us_count == 1:
                command = f"{clear_pat} {userid} {openid} 1"
            else:
                command = f"{clear_patplus} {userid} {openid} 1"
        elif utype == '医生':
            command = f"{clear_doc} {userid} {openid} {scan}"
        elif utype == '泰康用户':
            command = f"{clear_pat} {userid} {openid} 3"
        elif utype == '广盛康':
            command = f"{clear_pat} {userid} {openid} 5"
            up_sql = f"update gyy_cooperation_user_t set mobile={mobile}+100000000,name='作废卡' where mobile='{mobile}'"
            cur.execute(up_sql)
            con.commit()
        else:
            q_app_type = f"select id from gyy_td_part_info where app_name='{utype}'"
            cur.execute(q_app_type)
            app_type = cur.fetchone()[0]

            if us_count == 1:
                command = f"{clear_pat} {userid} {openid} {app_type}"
            else:
                command = f"{clear_patplus} {userid} {openid} {app_type}"

    # 执行清理命令
    stdin, stdout, stderr = conn.exec_command(command)
    out = stdout.read()
    conn.close()

    # 验证清理结果
    if utype == '销售':
        query_info = f"select mobile from gyy_sales_t where id={userid}"
    elif utype == '医生':
        query_info = f"select mobile from gyy_user_t t where t.id={userid}"
    else:
        query_info = f"select count(*) from gyy_user_third_t where third_account='{openid}' and apptype={app_type}"

    con.commit()
    cur.execute(query_info)
    comp = cur.fetchone()[0]
    cur.close()
    con.close()

    if comp == 0:
        result = '<div class ="alert alert-success">操作成功！请重新登录微信。</div>'
    elif comp == mobile:
        result = '<div class ="alert alert-danger">操作失败！请重试或手动清理！</div>'
    else:
        if openid == '无（APP注册用户）':
            result = '<div class ="alert alert-success">操作成功！无需退出微信。</div>'
        else:
            result = '<div class ="alert alert-success">操作成功！请重新登录微信。</div>'

    return HttpResponse(result)
