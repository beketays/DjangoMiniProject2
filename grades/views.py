import logging
from rest_framework import viewsets
from notifications.tasks import send_grade_notification
from .models import Grade
from .serializers import GradeSerializer
from rest_framework.permissions import IsAuthenticated
from users.permissions import IsTeacher, IsAdmin, IsStudent

logger = logging.getLogger("grades")

class GradeViewSet(viewsets.ModelViewSet):
    queryset = Grade.objects.all()
    serializer_class = GradeSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAuthenticated & (IsTeacher | IsAdmin)]
        elif self.action in ['list', 'retrieve']:
            permission_classes = [IsAuthenticated & (IsStudent | IsTeacher | IsAdmin)]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'teacher':
            return Grade.objects.filter(course__instructor=user)
        elif user.role == 'admin':
            return Grade.objects.all()
        elif user.role == 'student':
            return Grade.objects.filter(student__user=user)
        else:
            return Grade.objects.none()


    def perform_create(self, serializer):
        logger.info(f"Teacher {self.request.user.email} added a grade.")
        serializer.save(teacher=self.request.user)

    def create(self, validated_data):
        teacher = self.context['request'].user
        validated_data['teacher'] = teacher
        grade = Grade.objects.create(**validated_data)
        self.send_notification(grade)
        return grade

    def update(self, instance, validated_data):
        grade = super().update(instance, validated_data)
        self.send_notification(grade, updated=True)
        return grade

    def send_notification(self, grade, updated=False):
        student_email = grade.student.user.email
        course_name = grade.course.name
        grade_value = grade.grade
        if updated:
            subject = f'Grade Updated in {course_name}'
            message = f'Your grade has been updated to {grade_value} in {course_name}.'
        else:
            subject = f'New Grade Assigned in {course_name}'
            message = f'You have received a new grade: {grade_value} in {course_name}.'
        send_grade_notification.delay(student_email, course_name, grade_value)