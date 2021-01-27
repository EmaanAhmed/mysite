from django.contrib.auth import get_user_model
from channels.generic.websocket import  AsyncWebsocketConsumer
import json
from .models import Message
from channels.db import database_sync_to_async
from .views import get_messages_by_page, get_user_contact,get_current_chat
User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    async def fetch_messages(self, data):
        messages = await get_messages_by_page(data['chatId'],data['page'])
        content = {
            'command': 'messages',
            'messages':await self.messages_to_json(messages)
        }
        await self.send_message(content)
        current_chat = await get_current_chat(data['chatId'])
        await self.addSeenbyMember(current_chat,data['user_id'])

    @database_sync_to_async
    def addSeenbyMember(self,current_chat,user_id):
        current_chat.messages.latest('timestamp').seen_by.add(user_id)
        current_chat.save()        

    async def new_message(self, data):
        user_contact = await get_user_contact(data['from'])
        message = await self.createMessage(user_contact,data['message'])
        current_chat = await get_current_chat(data['chatId'])
        await self.addMessageToChat(current_chat,message)
        print('content:')
        content = {
            'command': 'new_message',
            'message':self.message_to_json(message)
        }
        print(content)
        await self.send_chat_message(content)


    @database_sync_to_async 
    def createMessage(self,user_contact,message): 
        msg = Message.objects.create(
            contact=user_contact, 
            content=message)
        return msg

    @database_sync_to_async
    def addMessageToChat(self,current_chat,message):
        current_chat.messages.add(message)
        current_chat.save()        
        
        

    @database_sync_to_async
    def messages_to_json(self, messages):
        result = []
        for message in messages:
            result.append(self.message_to_json(message))
        return result

    def message_to_json(self, message):
        return {
            'id': message.id,
            'contact': message.contact.user.username,
            'content': message.content,
            'timestamp': str(message.timestamp),
        }

    commands = {
        'fetch_messages': fetch_messages,
        'new_message': new_message
    }

    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
  

    async def receive(self, text_data):
        data = json.loads(text_data)
        await self.commands[data['command']](self, data)
        

    async def send_chat_message(self, message):    
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )

    async def send_message(self, message):
        await self.send(text_data=json.dumps(message))

    async def chat_message(self, event):
        message = event['message']
        await self.send(text_data=json.dumps(message))



class UsersConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user_name = self.scope['url_route']['kwargs']['user_name']
        await self.channel_layer.group_add(
            "users",
            self.channel_name
        )
        await self.update_user_status(self.user_name,True)
        status = {
            'command' : 'user_update',
            'status' : "true",
            'user_name': self.user_name
        } 
        await self.send_status(status)
        await self.accept()


    async def disconnect(self,close_code):
        self.user_name = self.scope['url_route']['kwargs']['user_name']
        await self.channel_layer.group_discard(
            "users",
            self.channel_name
        )
        await self.update_user_status(self.user_name,False)
        status = {
            'command' : 'user_update',
            'status' : "false",
            'user_name': self.user_name
        } 
        await self.send_status(status)

    async def send_status(self,status):
        await self.channel_layer.group_send(
            "users",
            {
                'type': 'user_status',
                'status': status
            }
        ) 

    async def user_status(self,event):
        status = event['status']
        await self.send(text_data=json.dumps(status))

    async def update_user_status(self,username,status):
        user_contact = await get_user_contact(username)
        await self.saveUserStatus(user_contact,status)

    @database_sync_to_async
    def saveUserStatus(self,user_contact,status):
        user_contact.status = status
        user_contact.save()


          
