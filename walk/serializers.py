from rest_framework import serializers

from dm.serializers import BaseSerializer
from walk.models import WalkingMate

class WalkingMateSerializer(BaseSerializer):
    host_name = serializers.SerializerMethodField()
    left_seat = serializers.SerializerMethodField()
    # add_user = serializers.IntegerField(required=False, write_only=True)

    def get_host_name(self,obj):
        return obj.host.username
    
    def get_left_seat(self,obj):
        try:
            return int(obj.people_num[0])-1-(obj.attending_user.count())
        except:
            return 0
        
    class Meta:
        model = WalkingMate
        fields = ['id','host','host_name', 'image', 'start_date', 'start_time', 'end_time', 'region', 
        'place', 'gender', 'size', 'people_num', 'contents', 'attending_user', 
        'status', 'created_at', 'updated_at', 'left_seat']
        
