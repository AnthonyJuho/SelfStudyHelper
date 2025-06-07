from django.shortcuts import redirect, render, HttpResponse
from .models import Students
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from myapp.models import Students, Room
from collections import defaultdict
import pandas as pd
import json
from django.db import transaction
from django.views.decorators.csrf import csrf_exempt
from .models import LeaveList, CheckList, Teacher, NightClass
from django.utils.dateparse import parse_datetime
# Create your views here.
def index(request):
    return HttpResponse('Welcome!')

def hello_view(request):
    return render(request, 'myapp/hello.html')

@login_required(login_url='/login/')
def student_search(request):
    student_id = request.GET.get('id')
    student = Students.objects.filter(id=student_id).first()
    return render(request, 'myapp/student_info.html', {'student': student})


@csrf_exempt
def login_view(request):
    if request.method == 'POST':
        username1 = request.POST['username']
        password1 = request.POST['password']
        user = authenticate(request, username=username1, password=password1)
        if user is not None:
            login(request, user)
            return redirect('main')
        else:
            return render(request, 'myapp/login.html', {'error': '아이디 또는 비밀번호가 틀렸습니다.'})
    return render(request, 'myapp/login.html')

def get_student_status(student_id, target_date=None):
    if not target_date:
        target_date = timezone.now().date()
    elif isinstance(target_date, str):
        target_date = datetime.strptime(target_date, '%Y-%m-%d').date()
        
    weekday_kor = ['월', '화', '수', '목', '금', '토', '일']
    day_kor = weekday_kor[target_date.weekday()]
    
    if LeaveList.objects.filter(hakbun=student_id, start_date=target_date).exists():
        return 'leave'

    if NightClass.objects.filter(id=student_id, class_day=day_kor).exists():
        return 'leave'

    if CheckList.objects.filter(id=student_id, check_date=target_date).exists():
        return 'absent'

    return 'normal'


def get_room_data(selected_date=None):
    rooms_dict = defaultdict(list)
    room_entries = Room.objects.all()
    room_names = room_entries.values_list('room_name', flat=True).distinct()

    for name in room_names:
        room_data = room_entries.filter(room_name=name)
        max_row = room_data.order_by('-room_row').first().room_row + 1
        max_col = room_data.order_by('-room_column').first().room_column + 1
        grid = [[('', '') for _ in range(max_col)] for _ in range(max_row)]

        for entry in room_data:
            row = entry.room_row
            col = entry.room_column
            if entry.seat == 'FT':
                student = Students.objects.filter(id=entry.id).first()
                stat = get_student_status(student.id, selected_date)
                student_name = student.name
                # print(student.id, student.id[3])
                # if int(student.id[3]) == 2:
                    # print(student_name.split()[0])
                    # student_name = student_name.split()[0]
                grid[row][col] = ('S', entry.id, student_name, stat)
            else:
                grid[row][col] = ('E', '', '')
        rooms_dict[name] = grid

    return dict(rooms_dict)


@csrf_exempt
def upload_excel(request):
    upload_results = []

    if request.method == 'POST' and request.FILES.get('excel_file'):
        excel_file = request.FILES['excel_file']

        try:
            df = pd.read_excel(excel_file, engine="openpyxl")

            with transaction.atomic():
                for _, row in df.iterrows():
                    exists = LeaveList.objects.filter(hakbun=row['hakbun'], start_date=row['start_date']).exists()

                    status = None
                    
                    if exists:
                        # upload_results.append({
                        #     'hakbun': row['hakbun'],
                        #     'kor_nm': row['kor_nm'],
                        #     'start_date': row['start_date'],
                        #     'status': '중복'
                        # })
                        status = '중복'
                    else:

                        LeaveList.objects.create(
                            num=row['num'],
                            aa_sabun=row['aa_sabun'],
                            aa_kor_nm=row['aa_kor_nm'],
                            reg_date=row['reg_date'],
                            ref_tea_sabun=row['ref_tea_sabun'],
                            gubun=row['gubun'],
                            hakbun=row['hakbun'],
                            kor_nm=row['kor_nm'],
                            gubun_nm=row['gubun_nm'],
                            symptom=row.get('symptom', ''),
                            reason=row.get('reason', ''),
                            place=row.get('place', ''),
                            start_date=row['start_date'],
                            start_time=row['start_time'],
                            end_date=row['end_date'],
                            end_time=row['end_time'],
                            approval_id=row['approval_id'],
                            approval_nm=row['approval_nm'],
                            status=row['status'],
                            status_style=row['status_style'],
                            status_nm=row['status_nm'],
                            ref_kor_nm=row['ref_kor_nm'],
                            buseo=row['buseo'],
                            all_check=row['all_check']
                        )
                        status='추가됨'
                    hakbun = row['hakbun']
                    start_date = row['start_date']
                    deleted = CheckList.objects.filter(id=hakbun, check_date=start_date).delete()
                    if deleted[0] > 0:
                        status = '무단이석 취소'

                    upload_results.append({
                        'hakbun': row['hakbun'],
                        'kor_nm': row['kor_nm'],
                        'start_date': row['start_date'],
                        'status': status
                    })

            return upload_results

        except Exception as e:
            print(e)
            return []  # 에러나면 빈 리스트 리턴

    return []  # 기본도 빈 리스트

from django.http import JsonResponse
from django.utils import timezone
from django.core.paginator import Paginator

@csrf_exempt
@login_required(login_url='/login/')
def mark_absent(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        student_id = data.get('id')
        selected_date = data.get('date')
        print('checked')
        try:
            check_date = datetime.strptime(selected_date, '%Y-%m-%d').date()
            
            student = Students.objects.get(id=student_id)
            CheckList.objects.create(
                grade = student.grade,
                id = student_id,
                name = student.name,
                content = '무단이석',
                check_date = check_date,
                class_field=str(student.grade)+'학년'+str(student.classno)+'반',
                class_teacher=Teacher.objects.get(class_year=student.grade,class_field=student.classno).teacher_name
            )
            return JsonResponse({'status': 'success'})
        except Exception as e:
            print(e)
            return JsonResponse({'status': 'error'})

@csrf_exempt
@login_required
def unmark_absent(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        student_id = data.get('id')
        selected_date = data.get('date')

        try:
            
            check_date = datetime.strptime(selected_date, '%Y-%m-%d').date()
            CheckList.objects.filter(id=student_id, content='무단이석', check_date=check_date).delete()
            return JsonResponse({'status': 'success'})
        except Exception as e:
            print(e)
            return JsonResponse({'status': 'error'})

from datetime import date

def get_admin_context(request):
    active_tab = request.GET.get('tab', 'upload')

    today = date.today().strftime('%Y-%m-%d')
    

    # LeaveList 조회
    leave_start = request.GET.get('leave_start', today)
    leave_end = request.GET.get('leave_end', today)
    leavelists = LeaveList.objects.all()
    if leave_start and leave_end:
        leavelists = leavelists.filter(start_date__range=[leave_start, leave_end])
    leave_paginator = Paginator(leavelists, 20)
    leave_page_number = request.GET.get('leave_page')
    leave_page_obj = leave_paginator.get_page(leave_page_number)

    # CheckList 조회
    check_start = request.GET.get('check_start', today)
    check_end = request.GET.get('check_end', today)
    checklists = CheckList.objects.all()
    if check_start and check_end:
        checklists = checklists.filter(check_date__range=[check_start, check_end])
    check_paginator = Paginator(checklists, 20)
    check_page_number = request.GET.get('check_page')
    check_page_obj = check_paginator.get_page(check_page_number)

    # 공통으로 넘길 context
    context = {
        'active_tab': active_tab,
        'leave_page_obj': leave_page_obj,
        'check_page_obj': check_page_obj,
        'leave_start': leave_start,
        'leave_end': leave_end,
        'check_start': check_start,
        'check_end': check_end,
    }
    return context

from datetime import datetime

@csrf_exempt
@login_required
def delete_absent(request):
    if request.method == 'POST':
        student_id = request.POST.get('id')
        check_date_raw = request.POST.get('check_date')
        check_date = None
        try:
            # 문자열 → 날짜 객체로 변환
            check_date = datetime.strptime(check_date_raw, "%B %d, %Y").date()
        except ValueError:
            # 포맷이 다르면 그냥 raw 사용
            check_date = check_date_raw
        print(check_date)
        if student_id and check_date:
            CheckList.objects.filter(id=student_id, check_date=check_date).delete()
        return redirect(f"/main/?tab=check&check_start={check_date}&check_end={check_date}")

@login_required(login_url='/login/')
@csrf_exempt
def main_view(request):
    user = request.user
    username = str(user)
    # print("1: "+str(timezone.now().date()))
    # print("2: "+str(LeaveList.objects.get(hakbun='24-078').end_date))
    
    if username == 'admin':
        upload_results = None  # 기본은 None

        if request.method == 'POST' and request.FILES.get('excel_file'):
            upload_results = upload_excel(request)

        context = get_admin_context(request)
        
        if upload_results:
            context['upload_results'] = upload_results

        return render(request, 'myapp/mainpage/admin.html', context)
    if username[0] == 't':
        selected_date = request.GET.get('date', timezone.now().date().strftime('%Y-%m-%d'))
        rooms = get_room_data(selected_date)
        return render(request, 'myapp/mainpage/teacher.html', {
            'rooms': rooms,
            'selected_date': selected_date
        })
        
    today = timezone.now().date()
    start = request.GET.get('start_date', today)
    end = request.GET.get('end_date', today)
    student_id = username
    checklists = CheckList.objects.filter(id=student_id, check_date__range=[start, end]).order_by('-check_date')
    if request.method == 'POST':
        for item in checklists:
            key = f"message_{item.check_date.strftime('%Y%m%d')}"
            msg = request.POST.get(key)
            print(msg)
            if msg is not None:
                print('message input detected')
                CheckList.objects.filter(id=item.id, check_date=item.check_date).update(message=msg)
        return redirect(f'/main/?start_date={start}&end_date={end}')

    return render(request, 'myapp/mainpage/student.html', {
        'checklists': checklists,
        'start_date': start,
        'end_date': end,
    })
    # return render(request, 'myapp/main.html', {'user': username.name})

# 자구 프로젝트 해야할 것:
# ✅1. views.py 에 있는 get_student_status 함수 고쳐야함. 지금은 이석신청자만 leave를 return하는데, 수업이 있는 학생들도 leave도 return해야함.
# 2. student.html 페이지를 만들어야함. -> 여기에 기능은 admin.html과 유사하게 무단이석 CheckList를 조회할 수 있게 해야함. (자기 것만)
# 3. student.html은 자신의 무단이석 옆에 message를 달 수 있게 해야함. -> 그리고 이것이 admin에게도 보여지도록 수정해야함.
# 4. 지금은 무단이석 체크가 당일밖에 안되는데, 만약 선생님이 다음날에 전날 무단이석표를 보고 옮길 수도 있음. 따라서 teacher.html에 체크하는 날짜를 정할 수 있게 해줘야함.
# 5. 현재 admin에서 자습이석자 명단 LeaveList를 업로드하면 DB에 들어가기만 하는데, 들어감과 동시에 그 날에 무단이석이 체크되어있으면 삭제해야함.