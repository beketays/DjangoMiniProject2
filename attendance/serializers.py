from rest_framework import serializers

from courses.models import Enrollment, Course
from courses.serializers import CourseSerializer
from students.models import Student
from students.serializers import StudentSerializer
from .models import Attendance

class AttendanceSerializer(serializers.ModelSerializer):

    student_id = serializers.PrimaryKeyRelatedField(queryset=Student.objects.all(), source='student', write_only=True)
    course_id = serializers.PrimaryKeyRelatedField(queryset=Course.objects.all(), source='course', write_only=True)
    student = StudentSerializer(read_only=True)
    course = CourseSerializer(read_only=True)

    class Meta:
        model = Attendance
        fields = ['id', 'student_id', 'student', 'course_id', 'course', 'date', 'status']

    def validate(self, attrs):
        user = self.context['request'].user
        student = attrs.get('student')
        course = attrs.get('course')
        date = attrs.get('date')

        if user.role not in ['teacher', 'admin']:
            raise serializers.ValidationError("You do not have permission to mark attendance.")

        if user.role == 'teacher':
            if course.instructor_id != user.id:
                raise serializers.ValidationError("You are not the instructor of this course.")

        if not Enrollment.objects.filter(student=student, course=course).exists():
            raise serializers.ValidationError("The student is not enrolled in this course.")

        if Attendance.objects.filter(student=student, course=course, date=date).exists():
            raise serializers.ValidationError("Attendance for this student, course, and date already exists.")

        return attrs

    def create(self, validated_data):
        return Attendance.objects.create(**validated_data)
