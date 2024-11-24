import logging
from rest_framework import viewsets
from .models import Attendance
from .serializers import AttendanceSerializer
from rest_framework.permissions import IsAuthenticated
from users.permissions import IsTeacher, IsAdmin, IsStudent

logger = logging.getLogger("attendance")

class AttendanceViewSet(viewsets.ModelViewSet):
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer

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
        if user.role == 'admin':
            return Attendance.objects.all()
        elif user.role == 'teacher':
            return Attendance.objects.filter(course__instructor=user)
        elif user.role == 'student':
            return Attendance.objects.filter(student__user=user)
        else:
            return Attendance.objects.none()

    def perform_create(self, serializer):
        attendance = serializer.save()
        logger.info(f"Teacher {self.request.user.username} marked attendance for student {attendance.student.user.username} in course {attendance.course.name} on {attendance.date}.")

    def perform_update(self, serializer):
        attendance = serializer.save()
        logger.info(f"Teacher {self.request.user.username} updated attendance for student {attendance.student.user.username} in course {attendance.course.name} on {attendance.date}.")

    def perform_destroy(self, instance):
        logger.info(f"Teacher {self.request.user.username} deleted attendance record {instance.id}.")
        instance.delete()
