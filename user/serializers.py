from rest_framework import serializers
from .models import User, PetProfile, UserProfile

EMAIL = ("@naver.com", "@gmail.com", "@kakao.com")

class PetProfileSerializer(serializers.ModelSerializer):

    pet_owner = serializers.SerializerMethodField()

    def get_pet_owner(self, obj):
        return obj.user.username

    class Meta:
        model = PetProfile
        fields = '__all__'


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = '__all__'

class UserSerializer(serializers.ModelSerializer):
    gender_choice = serializers.IntegerField(write_only=True, required=False)
    birthday_date = serializers.DateField(write_only=True, required=False)
    is_active_val = serializers.BooleanField(write_only=True, required=False)

    gender = serializers.SerializerMethodField()
    birthday = serializers.SerializerMethodField()
    show_active = serializers.SerializerMethodField()

    def get_gender(self, obj):
        try:
            return obj.userprofile.gender
        except:
            return f'없음'
    
    def get_birthday(self, obj):
        try:
            return obj.userprofile.birthday
        except:
            return f'없음'

    def show_active(self,obj):
        try:
            return obj.userprofile.is_active
        except:
            return f'없음'

    
    # def validate(self, data):

    #     if not data.get("email", "").endswith(EMAIL):
    #         raise serializers.ValidationError(
    #             detail={"error": "네이버, 구글, 카카오 이메일만 가입할 수 있습니다."}
    #         )
    #     if not len(data.get("password", "")) >= 6:
    #         raise serializers.ValidationError(
    #             detail={"error": "password의 길이는 6자리 이상이어야 합니다."}
    #         )

    def create(self, validated_data):
        gender_choice = validated_data.pop("gender_choice")
        birthday_date = validated_data.pop("birthday_date")
        is_active_val = validated_data.pop("is_active_val")
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        UserProfile.objects.create(
            user=user,
            gender=gender_choice,
            birthday=birthday_date,
            is_active=is_active_val,
        )
        return user

    class Meta:
        model = User
        fields = '__all__'

        extra_kwargs = {
            'password': {'write_only': True},
            'email': {
                'error_messages': {'required': '이메일을 입력해주세요', 'invalid': '알맞은 형식의 이메일을 입력해주세요'},
                'required': False
            },
        }

