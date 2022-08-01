from rest_framework import serializers
from dm.models import Message, Header
from datetime import datetime
from user.models import BaseModel, User


class BaseSerializer(serializers.ModelSerializer):
    date = serializers.SerializerMethodField()
    at_date = serializers.SerializerMethodField()
    at_time = serializers.SerializerMethodField()

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
        
    def get_at_date(self, obj):
        return obj.created_at.strftime('%Y년 %m월 %d일 %A')
        
    def get_at_time(self, obj):
        return obj.created_at.strftime('%p %I:%M')
        
    class Meta:
        model = BaseModel
        fields = "__all__"


# 어떤 사람이 가지고 있는 header id




class MessageSerializer(BaseSerializer):
    sender = serializers.SlugRelatedField(read_only=True, slug_field='username')
    
    class Meta:
        model = Message
        fields = ["sender", "message", "date", "at_date", "at_time"]


class HeaderSerializer(BaseSerializer):
    sender = serializers.SlugRelatedField(read_only=True, slug_field='username')
    receiver = serializers.SlugRelatedField(read_only=True, slug_field='username')
    messages = MessageSerializer(many=True, read_only=True, source='header')
    last_message = serializers.SerializerMethodField()
    sender_img = serializers.SerializerMethodField()
    receiver_img = serializers.SerializerMethodField()
    
    def get_sender_img(self, obj):
        profile_img = obj.sender.userprofile.profile_img
        return profile_img
        
    def get_receiver_img(self, obj):
        profile_img = obj.receiver.userprofile.profile_img
        return profile_img
    
    def get_last_message(self, obj):
        last_message = obj.header
        return MessageSerializer(last_message.last()).data

    class Meta:
        model = Header
        fields = ["id", "sender", "receiver", "last_message", "date", "messages", "sender_img", "receiver_img"]
        # fields = ["__all__"]
    
    


class UserHeaderSerializer(serializers.ModelSerializer):
    last_message = serializers.SerializerMethodField()

    def get_last_message(self, obj):
        last_message = obj.sender
        return HeaderSerializer(last_message.last()).data

    class Meta:
        model = User
        fields =  "__all__"

    
    
        