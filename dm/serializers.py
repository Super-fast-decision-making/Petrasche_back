from rest_framework import serializers
from dm.models import Message, Header
from datetime import datetime
from user.models import BaseModel, UserProfile

class BaseSerializer(serializers.ModelSerializer):
    date = serializers.SerializerMethodField()

    def get_date(self, obj):
        time = datetime.now()
        if (obj.created_at.date()==time.date()) and (obj.created_at.hour==time.hour):
            return str(time.minute-obj.created_at.minute)+"분전"
        elif obj.created_at.date()==time.date():
            return str(time.hour-obj.created_at.hour)+"시간전"
        elif obj.created_at.month==time.month:
            return  str(time.day-obj.created_at.day) + "일전"
        elif obj.created_at.year ==time.year:
            return str(time.month-obj.created_at.month) + "달전"
        else:
            return obj.created_at
    
    class Meta:
        model = BaseModel
        fields = "__all__"


class MessageSerializer(BaseSerializer):
    sender = serializers.SlugRelatedField(read_only=True, slug_field='username')
    
    class Meta:
        model = Message
        fields = ["sender", "message", "date"]


class HeaderSerializer(BaseSerializer):
    sender = serializers.SlugRelatedField(read_only=True, slug_field='username')
    receiver = serializers.SlugRelatedField(read_only=True, slug_field='username')
    messages = MessageSerializer(many=True, read_only=True, source='header')
    last_message = serializers.SerializerMethodField()
        
    class Meta:
        model = Header
        fields = ["id", "sender", "receiver", "last_message", "date", "messages"]
        
    def get_last_message(self, obj):
        last_message = obj.header
        return MessageSerializer(last_message.last()).data
        