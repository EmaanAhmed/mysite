from django.contrib.auth import get_user_model
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
import json
from .models import Message
from .views import get_messages_by_page, get_user_contact,get_current_chat

User = get_user_model()

class ChatConsumer(WebsocketConsumer):

    def fetch_messages(self, data):
        messages = get_messages_by_page(data['chatId'],data['page'])
        content = {
            'command': 'messages',
            'messages': self.messages_to_json(messages)
        }
        self.send_message(content)
        current_chat = get_current_chat(data['chatId'])
        current_chat.messages.latest('timestamp').seen_by.add(data['user_id'])
        current_chat.save()

    def new_message(self, data):
        user_contact =get_user_contact(data['from'])
        message = Message.objects.create(
            contact=user_contact, 
            content=data['message'])
        current_chat = get_current_chat(data['chatId'])
        current_chat.messages.add(message)
        current_chat.save()
        content = {
            'command': 'new_message',
            'message': self.message_to_json(message)
        }
        return self.send_chat_message(content)

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

    def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )
        self.accept()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )
  

    def receive(self, text_data):
        data = json.loads(text_data)
        self.commands[data['command']](self, data)
        

    def send_chat_message(self, message):    
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )

    def send_message(self, message):
        self.send(text_data=json.dumps(message))

    def chat_message(self, event):
        message = event['message']
        self.send(text_data=json.dumps(message))



class UsersConsumer(WebsocketConsumer):
    def connect(self):
        print('connect')
        self.user_name = self.scope['url_route']['kwargs']['user_name']
        print(self.user_name)
        async_to_sync(self.channel_layer.group_add)(
            "users",
            self.channel_name
        )
        self.update_user_status(self.user_name,True)
        status = {
            'command' : 'user_update',
            'status' : "true",
            'user_name': self.user_name
        } 
        self.send_status(status)
        self.accept()


    def disconnect(self,close_code):
        self.user_name = self.scope['url_route']['kwargs']['user_name']
        async_to_sync(self.channel_layer.group_discard)(
            "users",
            self.channel_name
        )
        self.update_user_status(self.user_name,False)
        status = {
            'command' : 'user_update',
            'status' : "false",
            'user_name': self.user_name
        } 
        self.send_status(status)

    def send_status(self,status):
        print('send_status')
        async_to_sync(self.channel_layer.group_send)(
            "users",
            {
                'type': 'user_status',
                'status': status
            }
        ) 

    def user_status(self,event):
        status = event['status']
        self.send(text_data=json.dumps(status))

    def update_user_status(self,username,status):
        user_contact =get_user_contact(username)
        user_contact.status = status
        user_contact.save()
          
