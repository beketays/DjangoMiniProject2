from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from users.models import User

@shared_task
def send_daily_attendance_reminders():
    students = User.objects.filter(role='student')
    for student in students:
        send_mail(
            'Daily Attendance Reminder',
            'Please remember to mark your attendance today.',
            'unit@kbtu.kz',
            [student.email],
            fail_silently=False,
        )

@shared_task
def send_grade_notification(student_email, course_name, grade_value):
    subject = f'New Grade Assigned in {course_name}'
    message = f'You have received a new grade: {grade_value} in {course_name}.'
    email_from = settings.DEFAULT_FROM_EMAIL
    recipient_list = [student_email]
    send_mail(subject, message, email_from, recipient_list)

@shared_task
def send_daily_report():
    from django.contrib.auth import get_user_model
    User = get_user_model()
    from grades.models import Grade
    from attendance.models import Attendance
    from django.utils import timezone
    from datetime import timedelta

    today = timezone.now().date()
    yesterday = today - timedelta(days=1)

    new_grades = Grade.objects.filter(date__date=yesterday)
    attendance_records = Attendance.objects.filter(date=yesterday)

    subject = 'Daily Report: Attendance and Grades'
    message = 'Summary of yesterday\'s attendance and grades:\n\n'

    message += 'Attendance Records:\n'
    for record in attendance_records:
        message += f'Student: {record.student.name}, Course: {record.course.name}, Status: {record.status}\n'

    message += '\nGrades Assigned:\n'
    for grade in new_grades:
        message += f'Student: {grade.student.name}, Course: {grade.course.name}, Grade: {grade.grade}\n'

    email_from = settings.DEFAULT_FROM_EMAIL
    admin_emails = User.objects.filter(role='admin').values_list('email', flat=True)
    recipient_list = list(admin_emails)

    send_mail(subject, message, email_from, recipient_list)

@shared_task
def send_weekly_student_updates():
    from django.contrib.auth import get_user_model
    User = get_user_model()
    from grades.models import Grade
    from attendance.models import Attendance
    from django.utils import timezone
    from datetime import timedelta

    today = timezone.now().date()
    last_week = today - timedelta(days=7)

    students = User.objects.filter(role='student')

    for student in students:
        student_profile = student.student
        grades = Grade.objects.filter(student=student_profile, date__gte=last_week)
        attendance_records = Attendance.objects.filter(student=student_profile, date__gte=last_week)

        subject = 'Your Weekly Performance Summary'
        message = f'Dear {student_profile.name},\n\nHere is your performance summary for the past week:\n\n'

        message += 'Attendance Records:\n'
        for record in attendance_records:
            message += f'Date: {record.date}, Course: {record.course.name}, Status: {record.status}\n'

        message += '\nGrades Received:\n'
        for grade in grades:
            message += f'Date: {grade.date}, Course: {grade.course.name}, Grade: {grade.grade}\n'

        email_from = settings.DEFAULT_FROM_EMAIL
        recipient_list = [student.email]
        send_mail(subject, message, email_from, recipient_list)