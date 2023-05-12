from django.contrib.auth.models import User
from rest_framework import serializers

from .models import ChatRoom, ChatMessage, ChatUser


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatUser
        fields = ['avatar', 'id', 'username']


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
            ChatUser.objects.filter(username=data['username']).first()
        except ChatUser.DoesNotExist:
            raise serializers.ValidationError('Пользователь с таким именем уже существует')
        try:
            ChatUser.objects.filter(email=data['email']).first()
        except ChatUser.DoesNotExist:
            raise serializers.ValidationError('Пользователь с таким email уже существует')
        return data

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        return ChatUser.objects.create_user(**{'username': validated_data['username'], 'email': validated_data['email'],
                                           'password': validated_data['password1']})
