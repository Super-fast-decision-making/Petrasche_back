from rest_framework import serializers
from tournament.models import TournamentAttendant, PetEventPeriod
from article.s3upload import upload as s3
from datetime import datetime

class TournamentAttendantSerializer(serializers.ModelSerializer):
    image_file = serializers.FileField(write_only=True, required=True)
    event = serializers.IntegerField(write_only=True, required=True)

    class Meta:
        model = TournamentAttendant
        fields = '__all__'
 
    def create(self, validated_data):
        image_file = validated_data.pop('image_file')
        event = validated_data.pop('event')
        user_id = validated_data.get('user_id')
        if image_file:
            image_url = s3(user_id,image_file)
            validated_data['image'] = image_url
            tournament_item = TournamentAttendant.objects.create(user_id=user_id, image=image_url)
            tournament_item.save()
            PetEventPeriod.objects.get(id=event).tournament_item.add(tournament_item)
        return tournament_item

class PetEventPeriodSerializer(serializers.ModelSerializer):
    pet = serializers.SerializerMethodField()
    rank_pet = serializers.SerializerMethodField()
    active= serializers.SerializerMethodField()
    event_start = serializers.SerializerMethodField(read_only=True)
    event_end = serializers.SerializerMethodField(read_only=True)

    def get_active(self, obj):
        now = datetime.now()
        if now > obj.start_time and now < obj.end_time:
            return "Participation"
        elif now < obj.start_time:
            return "Before"
        return "Expired"

    def get_event_start(self, obj):
        return obj.start_time.strftime("%Y년%m월%d일")
    
    def get_event_end(self, obj):
        return obj.end_time.strftime("%Y년%m월%d일")

    def get_pet(self, obj):
        pet = []
        for img in obj.tournament_item.all():
            doc = {
                'id': img.id,
                'image': img.image,
                'point': img.point,
            }
            pet.append(doc)
        return pet

    def get_rank_pet(self, obj):
        rank = obj.tournament_item.all().order_by('-point')[:5]
        pet = []
        for img in rank:
            doc = {
                'id': img.id,
                'image': img.image,
                'point': img.point,
            }
            pet.append(doc)
        return pet

    class Meta:
        model = PetEventPeriod
        fields = ["id", "event_name", "event_desc", "pet", "rank_pet", "start_time", "end_time", "event_start", "event_end", "active"]

        extra_kwargs = {
        }