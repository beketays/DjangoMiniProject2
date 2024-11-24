from django.db import models
from students.models import Student
from courses.models import Course

class Attendance(models.Model):
    """
    Represents an attendance record for a student in a specific course on a given date.

    Attributes:
        student (Student): The student whose attendance is being recorded.
        course (Course): The course for which attendance is being recorded.
        date (Date): The date of the attendance.
        status (str): The attendance status (e.g., present, absent, late).
    """

    STATUS_CHOICES = (
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('late', 'Late'),
    )

    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='attendance_records',
        help_text="The student whose attendance is being recorded."
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='attendance_records',
        help_text="The course for which attendance is being recorded."
    )
    date = models.DateField(
        help_text="The date of the attendance."
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        help_text="The attendance status (present, absent, late)."
    )
    class Meta:
        unique_together = ('student', 'course', 'date')

    def __str__(self):
        return f"{self.student} - {self.date}: {self.status}"
