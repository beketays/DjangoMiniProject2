from django.db import models
from users.models import User


class Student(models.Model):
    """
    Serializer for the Attendance model.

    Fields:
        id (int): Unique identifier for the attendance record.
        student (Student): The student whose attendance is recorded.
        course (Course): The course for which attendance is recorded.
        date (Date): The date of the attendance record.
        status (str): The attendance status (e.g., 'present', 'absent', 'late').
    """
    name = models.CharField(
        max_length=255,
        default="SomeName",
        help_text="The full name of the student."
    )
    student_id = models.IntegerField(
        help_text="A unique identifier for the student (e.g., school or system ID)."
    )
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='student_profile',
        help_text="The user account associated with the student."
    )
    dob = models.DateField(
        help_text="The date of birth of the student."
    )
    registration_date = models.DateField(
        auto_now_add=True,
        help_text="The date the student was registered in the system."
    )

    def __str__(self):
        return self.name + f" ({self.student_id})"
