from django.contrib.auth.models import User
from rest_framework import serializers

from .models import ChatRoom, ChatMessage


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']


class ChatRoomSerializer(serializers.ModelSerializer):
    autor = UserSerializer(many=False, read_only=True)
    users = UserSerializer(many=True, read_only=True)
    chat_size = serializers.IntegerField()

    class Meta:
        model = ChatRoom
        fields = ['id', 'name', 'autor', 'create_at', 'chat_size', 'users']


class ChatMessageSerializer(serializers.ModelSerializer):
    autor = UserSerializer(many=False, read_only=True)

    class Meta:
        model = ChatMessage
        fields = ['id', 'text', 'autor', 'is_event', 'create_at']


class UserRegisterSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=128, min_length=4)
    email = serializers.EmailField()
    password1 = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)

    def validate(self, data):
        data = super().validate(data)
        if not data.get('username') or not data.get('email') or not data.get('password1'):
            raise serializers.ValidationError('Не все обязательные поля заданы')
        if data['password1'] != data['password1']:
            raise serializers.ValidationError('Пароли не совпадают')
        try:
            User.objects.filter(username=data['username']).first()
        except User.DoesNotExist:
            raise serializers.ValidationError('Пользователь с таким именем уже существует')
        try:
            User.objects.filter(email=data['email']).first()
        except User.DoesNotExist:
            raise serializers.ValidationError('Пользователь с таким email уже существует')
        return data

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        print('validated_data\n\n', validated_data)
        return User.objects.create_user(**{'username': validated_data['username'], 'email': validated_data['email'],
                                           'password': validated_data['password1']})

