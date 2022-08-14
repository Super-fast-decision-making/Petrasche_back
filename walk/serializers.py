from rest_framework import serializers

from dm.serializers import BaseSerializer
from walk.models import WalkingMate
from user.models import UserProfile

class WalkingMateSerializer(BaseSerializer):
    host_name = serializers.SerializerMethodField()
    left_seat = serializers.SerializerMethodField()
    host_pic = serializers.SerializerMethodField()
    
    def get_host_pic(self,obj):
        try:
            user_profiles = UserProfile.objects.get(user=obj.host.id)
            return user_profiles.profile_img
        except:
            return f'https://cdn.pixabay.com/photo/2017/09/25/13/12/cocker-spaniel-2785074__480.jpg'
    

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
        'created_at', 'updated_at', 'left_seat', 'host_pic', 'deadeline_status']
        
