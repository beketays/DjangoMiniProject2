from django.test import TestCase
from unittest.mock import patch
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.urls import reverse
from users.models import User
from .models import Student

class StudentModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="student@kbtu.kz",
            username="student_user",
            password="password",
            role="student"
        )
        self.student = Student.objects.create(
            user=self.user,
            student_id=12345,
            name='John Doe',
            dob='2000-01-01'
        )

    def test_student_creation(self):
        self.assertEqual(self.student.student_id, 12345)
        self.assertEqual(self.student.name, 'John Doe')
        self.assertEqual(self.student.user.email, 'student@kbtu.kz')

    def test_student_str_representation(self):
        expected_str = f"{self.student.name} ({self.student.student_id})"
        self.assertEqual(str(self.student), expected_str)




class StudentAPITest(APITestCase):
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
        self.student = Student.objects.create(
            user=self.student_user,
            student_id=12345,
            name='John Doe',
            dob='2000-01-01'
        )


        self.client = APIClient()
        self.token_url = reverse('login')
        response = self.client.post(self.token_url, {
            'username': 'admin',
            'password': 'adminpass'
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        print(response.data)
        self.token = response.data['auth_token']
        print(self.token)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        self.url = reverse('student-list')



    def test_admin_can_retrieve_student_list(self):
        response = self.client.get(self.url, format='json')
        self.token = response.data.get('token')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, dict)
        self.assertIn('results', response.data)
        self.assertIsInstance(response.data['results'], list)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'John Doe')
        self.assertEqual(response.data['results'][0]['student_id'], 12345)

    def test_student_cannot_create_student(self):

        self.client.force_authenticate(user=self.student_user)
        data = {
            'user': self.student_user.id,
            'student_id': 54321,
            'name': 'Jane Doe',
            'dob': '2001-02-02'
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


from django.core.cache import cache


def test_student_list_caching(self):
    cache.clear()

    with self.assertNumQueries(2):
        response1 = self.client.get(self.url, format='json')
        self.assertEqual(response1.status_code, status.HTTP_200_OK)

    with self.assertNumQueries(0):
        response2 = self.client.get(self.url, format='json')
        self.assertEqual(response2.status_code, status.HTTP_200_OK)

    self.assertEqual(response1.data, response2.data)

