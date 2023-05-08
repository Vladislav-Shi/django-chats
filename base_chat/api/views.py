from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .models import ChatRoom, ChatMessage
from .serializers import ChatRoomSerializer, ChatMessageSerializer, UserRegisterSerializer


class ChatViews(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        context = ChatRoom.objects.filter(users=request.user)
        serializer = ChatRoomSerializer(context, many=True)
        return Response(serializer.data)

    def post(self, request):
        """Создать чат"""
        pass


class MessageHistory(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, chat_id: int, format=None):
        context = ChatMessage.objects.filter(chat_id=chat_id, chat__users=request.user)
        serializer = ChatMessageSerializer(context, many=True)
        return Response(serializer.data)

    def post(self, request):
        """Новое сообщение в чате"""
        pass


class UserAPIRegister(CreateAPIView):
    permission_classes = [AllowAny]
    """Класс регистрации пользователя. При успехе должен возвращать access и resresh токены"""
    serializer_class = UserRegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            user = User.objects.get(username=serializer.data.get('username'))
            refresh = RefreshToken.for_user(user)
            response_data = {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
            return Response(response_data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
