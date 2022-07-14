from dataclasses import field
from rest_framework import serializers
from dm.models import Message, Channel
from user.models import User


class MessageListSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField()

    class Meta:
        model = Message
        exclude = ['user']

    def get_username(self, obj):
        return obj.user.username


class ChannelSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source="owner.username")
    class Meta:
        model = Channel
        fields = ['name', 'owner', 'id', 'image_url']


class MessageCreateSerializer(serializers.ModelSerializer):    
    class Meta:
        model = Message
        fields = ['message']