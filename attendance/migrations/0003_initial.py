# Generated by Django 5.1.3 on 2024-11-24 15:57

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('attendance', '0002_initial'),
        ('students', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='attendance',
            name='student',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='attendance_records', to='students.student'),
        ),
        migrations.AlterUniqueTogether(
            name='attendance',
            unique_together={('student', 'course', 'date')},
        ),
    ]
