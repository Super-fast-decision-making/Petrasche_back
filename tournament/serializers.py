from rest_framework import serializers
from tournament.models import TournamentAttendant, PetEventPeriod
from article.s3upload import upload as s3

class TournamentAttendantSerializer(serializers.ModelSerializer):
    image_file = serializers.FileField(write_only=True, required=True)

    class Meta:
        model = TournamentAttendant
        fields = '__all__'
 
    def create(self, validated_data):
        image_file = validated_data.pop('image_file')
        user_id = validated_data.get('user_id')
        user_id = user_id.id
        if image_file:
            image_url = s3(user_id,image_file)
            validated_data['image'] = image_url
        return super().create(validated_data)

class PetEventPeriodSerializer(serializers.ModelSerializer):
    pet = serializers.SerializerMethodField()
    event_start = serializers.SerializerMethodField()
    event_end = serializers.SerializerMethodField()

    def get_event_start(self, obj):
        return obj.start_time.strftime("%Y년%m월%d일")
    
    def get_event_end(self, obj):
        return obj.end_time.strftime("%Y년%m월%d일")

    # def get_event_pet_img(self, obj):
        # return [img.image for img in obj.tournament_item.all()]

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


    class Meta:
        model = PetEventPeriod
        fields = ["id", "event_name", "event_desc", "pet", "event_start", "event_end"]

    