from rest_framework import serializers
from dm.models import Message, Header
from datetime import datetime
from user.models import BaseModel

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
    # sender_img = serializers.SerializerMethodField()
    # 
    # def get_sender_img(self, obj):
        # try:
            # return obj.userprofile.profile_img
        # except:
            # return f'https://cdn.pixabay.com/photo/2017/09/25/13/12/cocker-spaniel-2785074__480.jpg'
    
    class Meta:
        model = Header
        fields = ["id", "sender", "receiver", "last_message", "date", "messages"]
        # fields = ["__all__"]
    
    def get_last_message(self, obj):
        last_message = obj.header
        return MessageSerializer(last_message.last()).data
    
    
        