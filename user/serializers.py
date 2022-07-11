from rest_framework import serializers
from .models import User, UserFollowing, PetProfile

EMAIL = ("@naver.com", "@gmail.com", "@kakao.com")

class PetProfileSerializer(serializers.ModelSerializer):

    pet_owner = serializers.SerializerMethodField()

    def get_pet_owner(self, obj):
        return obj.user.username

    class Meta:
        model = PetProfile
        fields = '__all__'

class UserSerializer(serializers.ModelSerializer):

    def validate(self, data):

        if not data.get("email", "").endswith(EMAIL):
            raise serializers.ValidationError(
                detail={"error": "네이버, 구글, 카카오 이메일만 가입할 수 있습니다."}
            )
        if not len(data.get("password", "")) >= 6:
            raise serializers.ValidationError(
                detail={"error": "password의 길이는 6자리 이상이어야 합니다."}
            )


    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user

    class Meta:
        model = User
        fields = ['username', 'password', 'email', 'created_at', 'updated_at','latitude', 'longitude']

        extra_kwargs = {
            'password': {'write_only': True},
            'email': {
                'error_messages': {'required': '이메일을 입력해주세요', 'invalid': '알맞은 형식의 이메일을 입력해주세요'},
                'required': False
            },
        }
