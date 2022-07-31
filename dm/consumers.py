from datetime import datetime
import json
from channels.consumer import AsyncConsumer
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from dm.models import Message, Header
from user.models import User
# import locale
# locale.setlocale(locale.LC_TIME, 'ko_KR')

print("******************")
print("******************")
class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        print('connected')
        #url에 room_id를 받아서 가져온다.
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        print(self.room_id, "17")
        self.room_group_name = 'chat_%s' % self.room_id
        print("그룹네임", self.room_group_name)

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        print("disconnect", self.room_group_name)
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        
        received_data = json.loads(text_data)
        print("리시브",received_data)
        msg = received_data.get('message')
        sent_by_id = received_data.get('sent_by')
        send_to_id = received_data.get('send_to')
        header_id = received_data.get('header_id')

        if not msg:
            print('Error:: empty message')
            return False

        sender = await self.get_user_object(sent_by_id)
        receiver = await self.get_user_object(send_to_id)
        header_obj = await self.get_chatroom(header_id)
        
        if not sender:
            print('Error:: sent by user is incorrect')
        if not receiver:
            print('Error:: send to user is incorrect')
        if not header_obj:
            print('Error:: Header id is incorrect')

        await self.create_chat_message(header_obj, sender, msg)
        
        self_user = sender

        now_date = datetime.now().strftime('%Y년 %m월 %d일 %A')
        now_time = datetime.now().strftime('%p %I:%M')
        print(now_date, now_time)

        response = {
            'message': msg,
            'sender': self_user.id,
            'header_id': header_id,
            'date': now_date,
            'time': now_time,
        }
        
        # 현재그룹에 send
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'text': json.dumps(response)
            }
        )

    async def chat_message(self, event):
        text = json.loads(event['text'])
        message = text['message']
        now_time = text['time']
        now_date = text['date']
        header_id = text['header_id']
        sender = text['sender']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'time': now_time,
            'date': now_date,
            'header_id': header_id,
            'sender': sender
        }))


    @database_sync_to_async
    def get_user_object(self, user_id):
        qs = User.objects.filter(id=user_id)
        if qs.exists():
            obj = qs.first()
        else:
            obj = None
        return obj

    @database_sync_to_async
    def get_chatroom(self, header_id):
        qs = Header.objects.filter(id=header_id)
        if qs.exists():
            obj = qs.first()
        else:
            obj = None
        return obj

    @database_sync_to_async
    def create_chat_message(self, header, sender, msg):
        Message.objects.create(header=header, sender=sender, message=msg)
    


