import json
from channels.consumer import AsyncConsumer
from channels.db import database_sync_to_async
from dm.models import Message, Header
from user.models import User
from rest_framework_simplejwt.authentication import JWTAuthentication


class ChatConsumer(AsyncConsumer):
    
    async def websocket_connect(self, event):
        print('connected', event)
        user = self.scope['user']
        # user = self.scope.get('user')
        chat_room = f'user_chatroom_{user.id}'
        print(chat_room, user)
        self.chat_room = chat_room
        await self.channel_layer.group_add(
            chat_room,
            self.channel_name
        )
        await self.send({
            'type': 'websocket.accept'
        })

    async def websocket_receive(self, event):
        print('receive', event)
        received_data = json.loads(event['text'])
        print(received_data)
        msg = received_data.get('message')
        sent_by_id = received_data.get('sent_by')
        send_to_id = received_data.get('send_to')
        header_id = received_data.get('header_id')

        if not msg:
            print('Error:: empty message')
            return False

        sent_by_user = await self.get_user_object(sent_by_id)
        send_to_user = await self.get_user_object(send_to_id)
        header_obj = await self.get_header(header_id)
        if not sent_by_user:
            print('Error:: sent by user is incorrect')
        if not send_to_user:
            print('Error:: send to user is incorrect')
        if not header_obj:
            print('Error:: Header id is incorrect')

        await self.create_chat_message(header_obj, sent_by_user, msg)

        other_user_chat_room = f'user_chatroom_{send_to_id}'
        self_user = self.scope['user']
        response = {
            'message': msg,
            'sent_by': self_user.id,
            'header_id': header_id
        }

        await self.channel_layer.group_send(
            other_user_chat_room,
            {
                'type': 'chat_message',
                'text': json.dumps(response)
            }
        )

        await self.channel_layer.group_send(
            self.chat_room,
            {
                'type': 'chat_message',
                'text': json.dumps(response)
            }
        )


    async def websocket_disconnect(self, event):
        print('disconnect', event)


    async def chat_message(self, event):
        print('chat_message', event)
        await self.send({
            'type': 'websocket.send',
            'text': event['text']
        })
        

    @database_sync_to_async
    def get_user_object(self, user_id):
        qs = User.objects.filter(id=user_id)
        if qs.exists():
            obj = qs.first()
        else:
            obj = None
        return obj

    @database_sync_to_async
    def get_header(self, header_id):
        qs = Header.objects.filter(id=header_id)
        # qs = Header.objects.get_or_create(id=header_id)
        if qs.exists():
            obj = qs.first()
        else:
            obj = None
        return obj

    @database_sync_to_async
    def create_chat_message(self, header, sender, msg):
        Message.objects.create(header=header, sender=sender, message=msg)

