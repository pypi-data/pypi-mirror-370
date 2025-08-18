import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import ChatRoom, MessageChat
from django.contrib.auth import get_user_model
from asgiref.sync import sync_to_async


User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    @sync_to_async
    def is_user_in_chat_room(self, user, chat_room):
        if chat_room.users.filter(user__id=user.id).exists():
            return True
        return user == chat_room.user_1 or user == chat_room.user_2

    async def connect(self):
        user = self.scope["user"]
        if user.is_authenticated:
            self.user = user
            self.chat_room_id = self.scope['url_route']['kwargs']['chat_room_id']
            self.chat_room = await sync_to_async(ChatRoom.objects.get)(id=self.chat_room_id)

            if not await self.is_user_in_chat_room(user, self.chat_room):
                await self.close()
                return

            self.room_group_name = f"chat_{self.chat_room.id}"

            # Join room group
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )

            await self.accept()
        else:
            await self.close()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        user = self.scope["user"]
        if not user.is_authenticated:
            await self.close()
            return
            
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        sender_id = self.scope['user'].id
        # sender_id = text_data_json['sender_id']
        sender = await sync_to_async(User.objects.get)(id=sender_id)

        # Save message to database
        chat_message = await sync_to_async(MessageChat.objects.create)(
            chat_room=self.chat_room,
            sender=sender,
            text=message
        )

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': chat_message.text,
                'sender': sender.username
            }
        )

    async def chat_message(self, event):
        message = event['message']
        sender = event['sender']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'sender': sender
        }))