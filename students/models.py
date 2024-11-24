from django.db import models
from users.models import User


class Student(models.Model):
    name = models.CharField(max_length=255, default="SomeName")
    student_id = models.IntegerField()
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    dob = models.DateField()
    registration_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.name + f" ({self.student_id})"
