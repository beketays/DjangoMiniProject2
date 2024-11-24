from rest_framework import serializers

from users.models import User
from .models import Student
from users.serializers import UserSerializer

class StudentSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(write_only=True)
    user = UserSerializer(read_only=True)

    class Meta:
        model = Student
        fields = ['id', 'name', 'student_id','user_id' ,'user', 'dob', 'registration_date']

    def validate_user_id(self, value):
        try:
            user = User.objects.get(id=value)
            if user.role != 'student':
                raise serializers.ValidationError("User must have role 'student'.")
            if Student.objects.filter(user=user).exists():
                raise serializers.ValidationError("A Student profile for this user already exists.")
        except User.DoesNotExist:
            raise serializers.ValidationError("User does not exist.")
        return value

    def create(self, validated_data):
        user_id = validated_data.pop('user_id')
        user = User.objects.get(id=user_id)
        student = Student.objects.create(user=user, **validated_data)
        return student

    def update(self, instance, validated_data):
        validated_data.pop('user_id', None)  #
        return super().update(instance, validated_data)
