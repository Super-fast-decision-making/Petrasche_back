from dataclasses import field
from rest_framework import serializers
from dm.models import Message
from user.models import User

class MessageSerializer(serializers.ModelSerializer):
    sender = serializers.SlugRelatedField(many=False, slug_field='username', queryset=User.objects.all())
    receiver = serializers.SlugRelatedField(many=False, slug_field='username', queryset=User.objects.all())
    
    class Meta:
        model = Message
        field = "__all__"