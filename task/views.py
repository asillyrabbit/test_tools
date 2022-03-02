from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from config.models import EnvInfo, ComInfo
from task.models import Task, Status, User, Hours, Percent, Score
from django.db.models import Sum, Count, Q
from test_tools.common import OptRecord, MySSH, page_infos
from decimal import Decimal
import time


# 任务管理
def task(request):
    re = OptRecord(request)
    re.opt_record()

    f_hours = finish_hours(re.remote_ip)

    cur_month = str(time.strftime("%Y%m"))
    t_dates = Task.objects.select_related('date').filter(date__state=1).values('date__month').annotate(Count('date'))
    cur_day = str(time.strftime("%Y-%m-%d"))
    Task.objects.select_related('status').filter(~Q(status__name='已完成'), end__lt=cur_day).update(delay=0)
    Task.objects.select_related('status').filter(~Q(status__name='已完成'), end=cur_day).update(delay=2)

    dates = month_list('date', t_dates)
    status = Status.objects.all()

    if request.method != 'POST':
        state_id = Status.objects.get(name='进行中')
        tasks = Task.objects.select_related('date').filter(date__month=cur_month, status=state_id).order_by('end')
        def_sel = {'date': cur_month, 'state': '进行中'}
    else:
        q_month = request.POST['month']
        q_state = request.POST['state']
        tasks = get_tasks(q_state, q_month)

        def_sel = {'date': q_month, 'state': q_state}

    page_info = page_infos(tasks, 10, 1)

    context = {'page_info': page_info, 'dates': dates, 'def_sel': def_sel, 'status': status, 'f_hours': f_hours}
    return render(request, 'task/task.html', context)


def page(request, month, state, page):
    re = OptRecord(request)
    # re.opt_record()

    f_hours = finish_hours(re.remote_ip)

    t_dates = Task.objects.select_related('date').filter(date__state=1).values('date__month').annotate(Count('date'))
    dates = month_list('date', t_dates)
    status = Status.objects.all()

    tasks = get_tasks(state, month)

    page_info = page_infos(tasks, 10, page)

    def_sel = {'date': month, 'state': state}

    context = {'page_info': page_info, 'dates': dates, 'def_sel': def_sel, 'status': status, 'f_hours': f_hours}
    return render(request, 'task/page.html', context)


def get_tasks(state, month):
    state_id = Status.objects.get(name=state)
    if state == '已完成':
        tasks = Task.objects.select_related('date').filter(date__month=month, status=state_id).order_by('-updated')
    else:
        tasks = Task.objects.select_related('date').filter(date__month=month, status=state_id).order_by('end')
    return tasks


def update(requests):
    task_id = requests.GET['id']
    t_task = Task.objects.get(id=task_id)
    status_id = t_task.status_id

    re = OptRecord(requests)
    remote_ip = re.remote_ip
    tester = User.objects.filter(bindIp=remote_ip)

    if tester:
        tester = tester[0].name
        if status_id == 1:
            t_task.status_id = 2
            t_task.tester = tester
            button = f'<button type="button" class="opt-btn btn btn-secondary" disabled>认领</button>'
        else:
            t_task.status_id = 3
            if t_task.delay == 2:
                t_task.delay = 1
            button = f'<button type="button" class="opt-btn btn btn-secondary" disabled>完成</button>'
        t_task.save()
    else:
        tester = '路人'
        button = f'<button type="button" class="opt-btn btn btn-secondary" data-toggle="tooltip" ' \
                 'data-placement="top" title="仅支持测试人员操作！" disabled>无效</button>'

    result = {"button": button, "tester": tester}

    return JsonResponse(result)


# 积分统计
def score(request):
    re = OptRecord(request)
    re.opt_record()

    t_dates = Score.objects.select_related('month').filter(month__state=1).values('month__month').annotate(
        Count('month'))

    dates = month_list('month', t_dates)

    if request.method != 'POST':
        cur_month = str(time.strftime("%Y%m"))
    else:
        cur_month = request.POST['month']

    up_all_score(cur_month)

    sc = Score.objects.select_related('month').filter(month__month=cur_month).order_by('-score', 'desc')
    context = {'dates': dates, 'sc': sc, 'cur_month': cur_month}
    return render(request, 'task/score.html', context)


def com_score(rate):
    """
    计算分值
    com:compute
    """
    pt = Percent.objects.get(ident='threshold')
    max_rate = int(pt.percent * 100)
    max_score = pt.score
    min_rate = max_rate - max_score

    if rate >= max_rate:
        value = max_score
    elif min_rate <= rate < max_rate:
        t = max_rate - 1 - rate
        value = max_score - 1 - t
    else:
        value = 0

    return value


def up_h_score(tester, value, tester_hours, rate, hours):
    """
    更新单个测试人员的工时积分
    h:hours
    """
    sc = Score.objects.filter(tester=tester, month=hours.id, type='H')
    if rate > 100:
        desc = f'勤劳小蜜蜂（本月完成工时 {tester_hours} h，工作饱和度 {rate} %）'
    else:
        desc = f'本月完成工时 {tester_hours} h，工作饱和度 {rate} %'

    if sc and sc[0].desc != desc:
        sc[0].score = value
        sc[0].desc = desc
        sc[0].save()
    elif sc:
        return
    else:
        Score.objects.create(month_id=hours.id, tester=tester, score=value, desc=desc)


def up_b_score(tester, py_name, bug_infos, hours):
    """
    更新单个测试人员的bug积分
    h:bug
    """
    winner = bug_infos[0]
    names = bug_infos[1]

    sc = Score.objects.filter(tester=tester, month=hours.id, type='B')

    if sc:
        if py_name == winner:
            sc[0].score = 5
            desc = names[py_name].strip('，')
            sc[0].desc = f'捉虫小能手（{desc}）'
        elif (py_name != winner) and (py_name in names.keys()):
            sc[0].score = 0
            desc = names[py_name].strip('，')
            sc[0].desc = f'{desc}'
        else:
            return
        sc[0].save()
    else:
        if py_name == winner:
            desc = names[py_name].strip('，')
            desc = f'捉虫小能手（{desc}）'
            Score.objects.create(month_id=hours.id, tester=tester, score=5, desc=desc)
        elif (py_name != winner) and (py_name in names.keys()):
            desc = names[py_name].strip('，')
            Score.objects.create(month_id=hours.id, tester=tester, score=0, desc=desc)
        else:
            desc = '没有提交Bug'
            Score.objects.create(month_id=hours.id, tester=tester, score=0, desc=desc, type='B')


def up_all_score(q_month):
    """
    更新当前月所有测试人员的积分
    """
    hours = Hours.objects.get(month=q_month)
    bug_infos = st_bugs(q_month)

    all_tester = User.objects.all()
    for tester in all_tester:
        tester_hours, month_hours, rate = statistics(tester.name, hours)
        value = com_score(rate)
        up_h_score(tester.name, value, tester_hours, rate, hours)
        up_b_score(tester.name, tester.pinyin, bug_infos, hours)


def st_bugs(month):
    """
    st：统计
    """
    # 执行命令集
    server_info = eval(EnvInfo.objects.get(ident='chandao').info)
    query_commd = ComInfo.objects.get(ident='q_openedby').command
    query_commd = f'{query_commd} {month}'

    # 链接服务器
    myssh = MySSH(**server_info)
    conn = myssh.connect()

    # 执行重命名、统计操作
    stdin, stdout, stderr = conn.exec_command(query_commd)
    names = stdout.read().decode()
    names = eval(names)

    return names


# 公共方法
def finish_hours(remote_ip):
    """
    统计请求IP已完成工时，内部调用statistics函数完成统计。
    """
    tester = User.objects.filter(bindIp=remote_ip)
    cur_month = str(time.strftime("%Y%m"))
    hours = Hours.objects.get(month=cur_month)

    if tester:
        tester = tester[0].name
        tester_hours, month_hours, rate = statistics(tester, hours)
    else:
        tester_hours = 0
        month_hours = Decimal(hours.workDay) * Decimal(hours.dayHours)

    diff_hours = month_hours - Decimal(tester_hours)

    if diff_hours < 0:
        diff_hours = 0

    st_hours = {'tester_hours': tester_hours, 'diff_hours': diff_hours}
    return st_hours


def statistics(tester, hours):
    """
    统计单个测试人员的完成工时、饱和度
    hours：Hours表对象
    """
    state = Status.objects.get(name='已完成')

    hours_sum = Task.objects.values('date').annotate(Sum('hours')).filter(tester__icontains=tester, status=state.id,
                                                                          date=hours.id)
    delay_sum = Task.objects.values('date').annotate(Sum('hours')).filter(tester__icontains=tester, status=state.id,
                                                                          date=hours.id, delay=0)
    if delay_sum:
        pt = Percent.objects.get(ident='delay')
        percent = int(100 * pt.percent)
        d_time = delay_sum[0]['hours__sum']
        d_time = (Decimal(d_time) * (100 - percent)) / 100
        tester_hours = hours_sum[0]['hours__sum']
        tester_hours = Decimal(tester_hours) - d_time
    elif hours_sum:
        tester_hours = hours_sum[0]['hours__sum']
    else:
        tester_hours = 0

    month_hours = Decimal(hours.workDay) * Decimal(hours.dayHours)
    tester_hours = Decimal(tester_hours)

    rate = (tester_hours * 100) / (month_hours * 100)
    rate = round(rate, 2)
    rate = int(rate * 100)

    return tester_hours, month_hours, rate


def month_list(f_key, t_dates):
    """
    f_key:外键名
    t_dates：Task表、Score表返回的按月分组的结果对象
    """
    cur_month = str(time.strftime("%Y%m"))

    dates = []
    for date in t_dates:
        month = date[f'{f_key}__month']
        dates.append(month)
    if cur_month not in dates:
        dates.append(cur_month)
    return dates
