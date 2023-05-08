from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.generics import CreateAPIView, ListAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .models import ChatRoom, ChatMessage
from .serializers import ChatRoomSerializer, ChatMessageSerializer, UserRegisterSerializer, UserSerializer


class SingleChatViews(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, chat_id: int):
        context = ChatRoom.objects.get(id=chat_id)
        serializer = ChatRoomSerializer(context, many=False)
        return Response(serializer.data)


class ChatViews(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        """Инфо о доступном спсике чатов"""
        context = ChatRoom.objects.filter(users=request.user)
        serializer = ChatRoomSerializer(context, many=True)
        return Response(serializer.data)

    def post(self, request):
        """Создать чат"""
        chat = ChatRoom.objects.create(
            name=request.data['name'],
            autor=request.user,
        )
        try:
            users_username = [user['username'] for user in request.data['users']]
            chat_users = User.objects.filter(username__in=users_username)
            chat.users.set(chat_users)
            chat.users.add(request.user)
            chat.save()
            serializer = ChatRoomSerializer(chat, many=False)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except:
            chat.delete()
            return Response({'message': 'error'}, status=status.HTTP_400_BAD_REQUEST)


class MessageHistory(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, chat_id: int, format=None):
        context = ChatMessage.objects.filter(chat_id=chat_id, chat__users=request.user)
        serializer = ChatMessageSerializer(context, many=True)
        return Response(serializer.data)

    def post(self, request):
        ChatMessage.objects.create()
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


class UserAPI(ListAPIView):
    permission_classes = [IsAuthenticated]
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_queryset(self):
        queryset = User.objects.all()
        author = self.request.query_params.get('author', None)
        if author == '0':
            queryset = User.objects.exclude(username=self.request.user.username)
        return queryset
