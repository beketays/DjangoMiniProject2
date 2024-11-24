# courses/tests.py

from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from unittest.mock import patch
from django.urls import reverse
from rest_framework import status
from .models import Course
from django.core.cache import cache

User = get_user_model()


class CourseAPITest(TestCase):
    def setUp(self):
        self.admin_user = User.objects.create_user(
            email="admin@kbtu.kz",
            username="admin",
            password="adminpass",
            role="admin",
            is_staff=True,
            is_superuser=True
        )

        self.student_user = User.objects.create_user(
            email="student@kbtu.kz",
            username="student_user",
            password="studentpass",
            role="student"
        )

        self.teacher_user = User.objects.create_user(
            email="student1t@kbtu.kz",
            username="teacher_user",
            password="teacherpass",
            role="teacher"
        )

        self.course_data = {
            'name': 'Django for Beginners',
            'description': 'An introductory course on Django.',
            'instructor_id': self.teacher_user.id
        }

        self.client = APIClient()
        self.token_url = reverse('login')
        response = self.client.post(self.token_url, {
            'username': 'teacher_user',
            'password': 'teacherpass'
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.token = response.data.get('auth_token')
        self.assertIsNotNone(self.token, "Auth token not found in response.")

        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)

        self.url = reverse('course-list')


    def test_non_teacher_cannot_create_course(self):
        self.client.force_authenticate(user=self.student_user)

        response = self.client.post(self.token_url, {
            'username': 'teacher_user',
            'password': 'teacherpass'
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.token = response.data.get('auth_token')
        self.assertIsNotNone(self.token, "Auth token not found in response.")

        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)


        response = self.client.post(self.url, self.course_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.assertEqual(Course.objects.count(), 0)

    def test_teacher_can_update_course(self):
        course = Course.objects.create(
            name='Django Intermediate',
            description='An intermediate course on Django.',
            instructor=self.teacher_user
        )

        update_data = {
            'name': 'Django Intermediate Updated',
            'description': 'Updated description for the course.'
        }

        detail_url = reverse('course-detail', args=[course.id])

        response = self.client.patch(detail_url, update_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        course.refresh_from_db()
        self.assertEqual(course.name, update_data['name'])
        self.assertEqual(course.description, update_data['description'])


    def test_caching_on_course_list(self):
        Course.objects.create(
            name='Django Caching',
            description='Learn about caching in Django.',
            instructor=self.teacher_user
        )

        response1 = self.client.get(self.url, format='json')
        self.assertEqual(response1.status_code, status.HTTP_200_OK)
        self.assertIn('results', response1.data)
        self.assertEqual(len(response1.data['results']), 1)

        course = Course.objects.get()
        course.name = 'Django Caching Updated'
        course.save()

        response2 = self.client.get(self.url, format='json')
        self.assertEqual(response2.status_code, status.HTTP_200_OK)
        self.assertEqual(response2.data['results'][0]['name'], 'Django Caching')

        cache.clear()

        response3 = self.client.get(self.url, format='json')
        self.assertEqual(response3.status_code, status.HTTP_200_OK)
        self.assertEqual(response3.data['results'][0]['name'], 'Django Caching Updated')

