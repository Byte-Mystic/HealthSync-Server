from django.db import models
from Accounts.models import CustomUser


class Chats(models.Model):
    chat_id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    room_name = models.CharField(max_length=255)
    topic = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)


class AiChats(models.Model):
    user_chat_id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    chat_id = models.ForeignKey(Chats, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)


class Messages(models.Model):
    message_id = models.AutoField(primary_key=True)
    chat_id = models.ForeignKey(Chats, on_delete=models.CASCADE)
    sender_id = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    content = models.TextField()
    response = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)
