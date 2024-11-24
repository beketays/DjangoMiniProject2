from djoser.serializers import UserCreateSerializer as BaseUserCreateSerializer, UserSerializer as BaseUserSerializer
from .models import User

class UserCreateSerializer(BaseUserCreateSerializer):
    class Meta(BaseUserCreateSerializer.Meta):
        model = User
        fields = ('id', 'username', 'email', 'password', 'role')

class UserSerializer(BaseUserSerializer):
    """
    Serializer for the User model.

    Fields:
        id (int): Unique identifier for the user.
        username (str): Username of the user.
        email (str): Email address of the user.
        role (str): Role of the user (e.g., admin, teacher, student).
    """
    class Meta(BaseUserSerializer.Meta):
        model = User
        fields = ('id', 'username', 'email', 'role')
