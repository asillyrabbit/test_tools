from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from task.models import Task, Status, User, Hours
from django.db.models import Sum, Count
from test_tools.common import OptRecord
import time


# Create your views here.
def task(request):
    re = OptRecord(request)
    re.opt_record()

    st_hours = statistics(re.remote_ip)

    t_dates = Task.objects.select_related('date').filter(date__state=1).values('date__month').annotate(Count('date'))

    dates = []
    for date in t_dates:
        month = date['date__month']
        dates.append(month)

    status = Status.objects.all()

    if request.method != 'POST':
        cur_month = str(time.strftime("%Y%m"))
        tasks = Task.objects.select_related('date').filter(date__month=cur_month, status='2')

        def_sel = {'date': cur_month, 'state': '进行中'}
        context = {'tasks': tasks, 'dates': dates, 'def_sel': def_sel, 'status': status, 'st_hours': st_hours}
        return render(request, 'task/task.html', context)
    else:
        q_month = request.POST['month']
        q_state = request.POST['state']
        state_id = Status.objects.get(name=q_state)
        tasks = Task.objects.select_related('date').filter(date__month=q_month, status=state_id)
        def_sel = {'date': q_month, 'state': q_state}
        context = {'tasks': tasks, 'dates': dates, 'def_sel': def_sel, 'status': status, 'st_hours': st_hours}
        return render(request, 'task/task.html', context)


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
            button = f'<button type="button" class="opt-btn btn btn-secondary" disabled>完成</button>'
        t_task.save()
    else:
        # tester = t_task.tester
        tester = '路人'
        button = f'<button type="button" class="opt-btn btn btn-secondary" data-toggle="tooltip" ' \
                 'data-placement="top" title="仅支持测试人员操作！" disabled>无效</button>'

    result = {"button": button, "tester": tester}

    return JsonResponse(result)


def statistics(remote_ip):
    from decimal import Decimal
    tester = User.objects.filter(bindIp=remote_ip)

    if tester:
        tester = tester[0].name
        state = Status.objects.get(name='已完成')
        hours_sum = Task.objects.values('tester').annotate(Sum('hours')).filter(tester=tester, status=state.id)
        if hours_sum:
            tester_hours = hours_sum[0]['hours__sum']
        else:
            tester_hours = 0
    else:
        tester_hours = 0

    cur_month = str(time.strftime("%Y%m"))
    h = Hours.objects.get(month=cur_month)
    # 当月工时 = 工作日 * 日工时 - 2天（上线、会议缓冲时间）
    month_hours = (Decimal(h.workDay) - Decimal(2)) * Decimal(h.dayHours)
    diff_hours = month_hours - Decimal(tester_hours)

    if diff_hours < 0:
        diff_hours = 0

    st_hours = {'tester_hours': tester_hours, 'diff_hours': diff_hours}
    return st_hours
