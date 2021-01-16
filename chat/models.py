from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()



class Contact(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    # friends = models.ManyToManyField('self',blank=True)
    status = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username

class Message(models.Model):
    contact = models.ForeignKey(Contact, related_name="messages", on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    seen_by = models.ManyToManyField(Contact, related_name="seen_by")
    
    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return self.contact.user.username


class Chat(models.Model):
    participants = models.ManyToManyField(Contact, related_name="chats")
    messages = models.ManyToManyField(Message,blank=True)
    
    def __str__(self):
        return "{}".format(self.pk)