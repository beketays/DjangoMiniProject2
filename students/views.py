import logging

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated
from django.core.cache import cache
from rest_framework.response import Response
from students.models import Student
from students.serializers import StudentSerializer
from users.permissions import IsStudent, IsAdmin, IsTeacher, IsAdminOrTeacher

logger = logging.getLogger("students")


class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['registration_date']
    ordering_fields = ['name', 'registration_date', 'dob']
    ordering = ['name']

    def get_permissions(self):
        if self.action in ['retrieve', 'update', 'partial_update']:
            permission_classes = [IsAuthenticated & IsStudent | IsAdmin]
        elif self.action in ['create', 'destroy']:
            permission_classes = [IsAuthenticated & IsAdmin]
        elif self.action in ['list']:
            permission_classes = [IsAuthenticated & IsAdminOrTeacher]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]


    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return Student.objects.all()
        elif user.role == 'student':
            return Student.objects.filter(user=user)
        elif user.role == 'teacher':
            return Student.objects.filter(enrollments__course__instructor=user).distinct()
        return Student.objects.none()

    def perform_create(self, serializer):
        logger.info(f"Admin {self.request.user.email} created a student record.")
        serializer.save()

    def perform_update(self, serializer):
        logger.info(f"User {self.request.user.email} updated student record {serializer.instance.id}.")
        serializer.save()

    def retrieve(self, request, *args, **kwargs):
        cache_key = f'student_{kwargs["pk"]}'
        data = cache.get(cache_key)
        if data:
            logger.info(f"Student {kwargs['pk']} cache hit")
            return Response(data)
        else:
            response = super().retrieve(request, *args, **kwargs)
            cache.set(cache_key, response.data, timeout=60*15)
            logger.info(f"Student {kwargs['pk']} cache miss - data cached")
            return response

    def perform_update(self, serializer):
        super().perform_update(serializer)
        cache_key = f'student_{serializer.instance.pk}'
        cache.delete(cache_key)
        logger.info(f"Student {serializer.instance.pk} cache invalidated due to update")