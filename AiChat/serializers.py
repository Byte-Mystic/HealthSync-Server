from rest_framework import serializers
from .models import Chats, Messages


class ChatsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chats
        fields = "__all__"


class MessagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Messages
        fields = "__all__"
