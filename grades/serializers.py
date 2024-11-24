from rest_framework import serializers

from courses.models import Course
from courses.serializers import CourseSerializer
from students.models import Student
from students.serializers import StudentSerializer
from users.models import User
from users.serializers import UserSerializer
from .models import Grade

class GradeSerializer(serializers.ModelSerializer):
    student_id = serializers.PrimaryKeyRelatedField(queryset=Student.objects.all(), source='student', write_only=True)
    course_id = serializers.PrimaryKeyRelatedField(queryset=Course.objects.all(), source='course',write_only=True)
    teacher_id = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), source='teacher',write_only=True)
    student = StudentSerializer(read_only=True)
    course = CourseSerializer(read_only=True)
    teacher = UserSerializer(read_only=True)

    class Meta:
        model = Grade
        fields = ['id', 'student_id', 'student', 'course_id', 'course', 'grade', 'date', 'teacher_id', 'teacher']

    def validate(self, attrs):
        teacher = self.context['request'].user
        teacher_id = self.initial_data.get('teacher_id')
        student = attrs.get('student')
        course = attrs.get('course')
        grade_value = attrs.get('grade')

        # Ensure the user is a teacher
        if teacher.role != 'teacher':
            raise serializers.ValidationError("Only teachers can assign grades.")

        # Ensure the teacher is the instructor of the course
        if teacher_id != teacher.id:
            raise serializers.ValidationError("You can only assign grades from your name.")

        # Ensure the teacher is the instructor of the course
        if course.instructor != teacher:
            raise serializers.ValidationError("You are not the instructor of this course.")

        if not course.enrollments.filter(student=student).exists():
            raise serializers.ValidationError("The student is not enrolled in this course.")

        if grade_value < 0:
            raise serializers.ValidationError("Grade must be a positive number.")

        return attrs

    def create(self, validated_data):
        teacher = self.context['request'].user
        validated_data['teacher'] = teacher
        return Grade.objects.create(**validated_data)