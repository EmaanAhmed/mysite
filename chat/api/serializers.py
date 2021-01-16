from rest_framework import serializers
from django.contrib.auth import get_user_model

from chat.models import Chat, Contact, Message


User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id','username']

class ContactSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    class Meta:
        model = Contact
        fields = ('__all__')

class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ('__all__')

class ChatSerializer(serializers.ModelSerializer):
    participants = ContactSerializer(many=True)
    last_message = serializers.SerializerMethodField()
    class Meta:
        model = Chat
        exclude = ['messages']
    def get_last_message(self,obj):
        return MessageSerializer(obj.messages.last()).data



 