from rest_framework import serializers
from .models import User, UserFollowing


# class UserFollowingSerializer(serializers.ModelSerializer):
#     class Meta:
#         model=UserFollowing
#         fields=['user_id', 'following_user_id', 'created_at']

class UserSerializer(serializers.ModelSerializer):

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
