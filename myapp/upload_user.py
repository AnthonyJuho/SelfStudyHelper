from django.contrib.auth.models import User
from myapp.models import Students, Teacher

def migrate_old_users():
    for old_user in Students.objects.all():
        if not User.objects.filter(username=old_user.id).exists():
            User.objects.create_user(
                username=old_user.id,
                password=old_user.id  # 비밀번호가 해시화 안 되어 있다면 해시 처리함
            )

def add_teacher_and_admin():
    for t in Teacher.objects.all():
        if not User.objects.filter(username=t.teacher_name).exists():
            User.objects.create_user(
                username='t'+str(t.class_year)+'-'+str(t.class_field),
                password='t'+str(t.class_year)+'-'+str(t.class_field)
            )
    if not User.objects.filter(username='admin').exists():
        User.objects.create_user(username='admin',password='admin')

def change_admin_password():
    if User.objects.filter(username='admin').exists():
        User.objects.filter(username='admin').delete()
    User.objects.create_user(username='admin',password='admin')

def do_all():
    migrate_old_users()
    add_teacher_and_admin()