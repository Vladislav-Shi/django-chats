from dataclasses import dataclass
from enum import Enum
from typing import TypedDict, Optional

from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer

from api.models import ChatRoom, ChatMessage
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.authentication import JWTAuthentication


class ChatEventType(Enum):
    INVITE = 'INVITE'  # Приглашение в чат
    NEW_MESSAGE = 'chat_message'  # новое сообщение
    BAN_USER = 'BAN_USER'  # Если банит пользователя
    LEAVE = 'LEAVE'  # Самовольный выход пользователя с чата
    NOTIFICATION = 'NOTIFICATION'  # сисетмное уведомление

    @classmethod
    def has_value(cls, value):
        return value in cls._value2member_map_


class JsonResponse(TypedDict):
    pass


@dataclass
class JsonRequest:
    type: ChatEventType
    message: str
    payload: Optional[dict] = None


class ChatConsumer(AsyncJsonWebsocketConsumer):

    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.room_name = None
        self.room_group_name = None
        self.room = None

    async def connect(self):
        print('\nconnect sucsessfull\n')
        if self.scope["user"] == AnonymousUser():
            await self.close()
            return
        await self.accept()
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room = await sync_to_async(ChatRoom.objects.get)(pk=self.room_name)
        await self.channel_layer.group_add(
            self.room_name,
            self.channel_name,
        )

    async def disconnect(self, context):
        if self.room_name is not None:
            await self.channel_layer.group_discard(
                self.room_name,
                self.channel_name,
            )

    async def receive_json(self, content):
        print('\n\ncontent', content)
        if not ChatEventType.has_value(content["type"]):
            raise ValueError(f'content["type"] is not valid to ChatEventType')
        msg = await sync_to_async(ChatMessage.objects.create)(
            text=content['message'],
            chat_id=int(content['chat_id']),
            autor=self.scope["user"],
        )
        request_dict = JsonRequest(
            type=content["type"],
            message=content['message'],
        )
        if request_dict.type == 'chat_message':
            await self.channel_layer.group_send(
                self.room_name,
                {
                    'type': 'chat_message',
                    'message': msg.text,
                    'autor': str(self.scope["user"].username),
                    'date': str(msg.create_at)
                }
            )

    async def chat_message(self, event):
        print('work')
        await self.send_json(event)
