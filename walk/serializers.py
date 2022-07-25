from rest_framework import serializers

from dm.serializers import BaseSerializer
from walk.models import WalkingMate

class WalkingMateSerializer(BaseSerializer):
    host_name = serializers.SerializerMethodField()

    def get_host_name(self,obj):
        return obj.host.username

    class Meta:
        model = WalkingMate
        fields = ['host','host_name', 'image', 'date', 'start_time', 'end_time', 'region', 
        'place', 'gender', 'size', 'people_num', 'contents', 'attending_user', 
        'status', 'created_at', 'updated_at']
        
