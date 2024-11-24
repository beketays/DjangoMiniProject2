import logging

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from .models import Course, Enrollment
from .serializers import CourseSerializer, EnrollmentSerializer
from rest_framework.permissions import IsAuthenticated
from users.permissions import IsTeacher, IsAdmin, IsStudent
from rest_framework import filters
from django.core.cache import cache
from rest_framework.response import Response

logger = logging.getLogger("courses")

class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['instructor__username']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'instructor__username']

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAuthenticated & (IsTeacher | IsAdmin)]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return Course.objects.all()
        elif user.role == 'teacher':
            return Course.objects.filter(instructor=user)
        elif user.role == 'student':
            return Course.objects.filter(enrollments__student__user=user).distinct()
        else:
            return Course.objects.none()

    def perform_create(self, serializer):
        course = serializer.save()
        cache.delete(f'courses_list_{self.request.user.id}')
        logger.info(f"User {self.request.user.email} created course {course.id}.")

    def perform_update(self, serializer):
        course = serializer.save()
        cache.delete(f'courses_list_{self.request.user.id}')
        logger.info(f"User {self.request.user.email} updated course {course.id}.")

    def perform_destroy(self, instance):
        super().perform_destroy(instance)
        cache.delete(f'courses_list_{self.request.user.id}')
        logger.info(f"User {self.request.user.email} deleted course {instance.id}.")

    def list(self, request, *args, **kwargs):
        user = request.user
        cache_key = f'courses_list_{user.id}'
        data = cache.get(cache_key)
        if data:
            logger.info(f"Courses list cache hit for user {user.email}")
            return Response(data)
        else:
            response = super().list(request, *args, **kwargs)
            cache.set(cache_key, response.data, timeout=60 * 15)
            logger.info(f"Courses list cache miss for user {user.email} - data cached")
            return response

class EnrollmentViewSet(viewsets.ModelViewSet):
    queryset = Enrollment.objects.all()
    serializer_class = EnrollmentSerializer

    def get_permissions(self):
        if self.action in ['create', 'destroy']:
            permission_classes = [IsAuthenticated & (IsStudent | IsAdmin)]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return Enrollment.objects.all()
        elif user.role == 'teacher':
            return Enrollment.objects.filter(course__instructor=user)
        elif user.role == 'student':
            return Enrollment.objects.filter(student__user=user)
        else:
            return Enrollment.objects.none()

    def perform_create(self, serializer):
        enrollment = serializer.save()
        course_name = enrollment.course.name
        logger.info(f"User {self.request.user.username} enrolled to course '{course_name}'.")

    def perform_destroy(self, instance):
        course_name = instance.course.name
        logger.info(f"User {self.request.user.username} unenrolled from course '{course_name}'.")
        instance.delete()