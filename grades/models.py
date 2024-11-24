from django.db import models
from students.models import Student
from courses.models import Course
from users.models import User

class Grade(models.Model):
    """
    Represents a grade assigned to a student for a specific course.

    Attributes:
        student (Student): The student receiving the grade.
        course (Course): The course for which the grade is assigned.
        grade (Decimal): The numerical score of the grade (e.g., 95.00).
        date (Date): The date when the grade was assigned.
        teacher (User): The teacher who assigned the grade.
    """
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='grades')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='grades')
    grade = models.DecimalField(max_digits=5, decimal_places=2)
    date = models.DateField(auto_now_add=True)
    teacher = models.ForeignKey(User, limit_choices_to={'role': 'teacher'}, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.student} - {self.course}: {self.grade}"