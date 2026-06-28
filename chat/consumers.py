# chat/consumers.py

import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Message
from django.contrib.auth.models import User
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        if not self.scope["user"].is_authenticated:
            await self.close()
            return
            
        self.user = self.scope['user']
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'
        
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_status',
                'username': self.user.username,
                'status': 'online'
            }
        )
        
        last_messages = await self.get_last_messages(self.room_name)
        await self.send(text_data=json.dumps({
            'type': 'history',
            'messages': last_messages
        }))


    async def disconnect(self, close_code):
        if self.user.is_authenticated:
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'user_status',
                    'username': self.user.username,
                    'status': 'offline'
                }
            )

        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_type = text_data_json.get('type')
        
        username = self.user.username

        if message_type == 'typing':
             await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'user_typing',
                    'username': username,
                    'is_typing': text_data_json['is_typing']
                }
            )
             return

        message = text_data_json.get('message')

        if message and message.strip():
            await self.save_message(username, self.room_name, message)

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message,
                    'username': username,
                    'timestamp': timezone.now().strftime("%H:%M") 
                }
            )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message': event['message'],
            'username': event['username'],
            'timestamp': event['timestamp']
        }))

    async def user_status(self, event):
        await self.send(text_data=json.dumps({
            'type': 'user_status',
            'username': event['username'],
            'status': event['status']
        }))

    async def user_typing(self, event):
        if event['username'] != self.user.username:
            await self.send(text_data=json.dumps({
                'type': 'user_typing',
                'username': event['username'],
                'is_typing': event['is_typing']
            }))

    @database_sync_to_async
    def save_message(self, username, room, text):
        user = User.objects.get(username=username)
        Message.objects.create(author=user, room=room, text=text)

    @database_sync_to_async
    def get_last_messages(self, room):
        messages = Message.objects.filter(room=room).order_by('-created_at')[:20]
        return [{'username': m.author.username, 'message': m.text, 'timestamp': m.created_at.strftime("%H:%M")} for m in reversed(messages)]