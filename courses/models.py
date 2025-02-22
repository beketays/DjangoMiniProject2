
from django.db import models
from users.models import User
from students.models import Student

class Course(models.Model):
    """
    Represents an educational course within the Student Management System.

    Attributes:
        name (str): The name of the course.
        description (str): Detailed information about the course content.
        instructor (User): The teacher responsible for the course.
    """
    name = models.CharField(max_length=100)
    description = models.TextField()
    instructor = models.ForeignKey(User, limit_choices_to={'role': 'teacher'}, on_delete=models.CASCADE, related_name='courses')

    def __str__(self):
        return self.name

class Enrollment(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    enrollment_date = models.DateField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'course')