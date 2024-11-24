from rest_framework import serializers

from students.models import Student
from students.serializers import StudentSerializer
from .models import Course, Enrollment
from users.serializers import UserSerializer

class CourseSerializer(serializers.ModelSerializer):
    """
    Serializer for the Course model.

    Fields:
    - `id`: Unique identifier for the course.
    - `name`: The name of the course.
    - `description`: A detailed description of the course.
    - `instructor`: The teacher responsible for the course.
    - `instructor_id`: The ID of teacher responsible for the course.

    """
    instructor_id = serializers.IntegerField(write_only=True)
    instructor = UserSerializer(read_only=True)

    class Meta:
        model = Course
        fields = ['id', 'name', 'description', 'instructor_id','instructor']

    def get_enrollments(self, obj):
        enrollments = obj.enrollments.select_related('student')
        return EnrollmentSerializer(enrollments, many=True).data

class EnrollmentSerializer(serializers.ModelSerializer):
    student = StudentSerializer(read_only=True)
    course = CourseSerializer(read_only=True)
    student_id = serializers.PrimaryKeyRelatedField(queryset=Student.objects.all(), source='student', write_only=True)
    course_id = serializers.PrimaryKeyRelatedField(queryset=Course.objects.all(), source='course', write_only=True)

    class Meta:
        model = Enrollment
        fields = ['id', 'student', 'course', 'student_id', 'course_id', 'enrollment_date']

    def validate(self, attrs):
        user = self.context['request'].user
        student = attrs.get('student')
        course = attrs.get('course')

        if user.role == 'student':
            try:
                user_student = user.student_profile
            except Student.DoesNotExist:
                raise serializers.ValidationError("Student profile does not exist for this user.")

            if student != user_student:
                raise serializers.ValidationError("Students can only enroll themselves into courses.")

        if Enrollment.objects.filter(student=student, course=course).exists():
            raise serializers.ValidationError("Student is already enrolled in this course.")


        return attrs

    def create(self, validated_data):
        enrollment = Enrollment.objects.create(**validated_data)
        return enrollment
