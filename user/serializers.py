from rest_framework import serializers
from .models import User, UserFollowing


class UserFollowingSerializer(serializers.ModelSerializer):
    class Meta:
        model=UserFollowing
        fields=['user_id', 'following_user_id', 'created_at']



class UserSerializer(serializers.ModelSerializer):
    user_following= UserFollowingSerializer(read_only=True)
    print(user_following)



    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user

    class Meta:
        model = User
        fields = ['username', 'password','email', 'created_at', 'updated_at']
