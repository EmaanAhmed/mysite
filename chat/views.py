from django.contrib.auth import get_user_model
from django.shortcuts import render, get_object_or_404
from .models import Chat, Contact, Message
from channels.db import database_sync_to_async

User = get_user_model()


@database_sync_to_async
def get_messages_by_page(chatId,page = 1):
    # chat = get_object_or_404(Chat,id=chatId)
    start = 20 * (page - 1)
    end = 20 * page
    return Message.objects.filter(chat__id=chatId).order_by('-timestamp')[start:end]

@database_sync_to_async
def get_user_contact(username):
    user = get_object_or_404(User,username=username)
    contact =  get_object_or_404(Contact,user=user)
    return contact

@database_sync_to_async
def get_current_chat(chatId):
    return get_object_or_404(Chat,id=chatId) 