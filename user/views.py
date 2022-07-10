from rest_framework.views import APIView
from rest_framework import status, permissions
from rest_framework.response import Response

from .serializers_jwt import TokenObtainPairSerializer
from .serializers import UserSerializer

from .models import User, UserFollowing

from rest_framework_simplejwt.views import TokenObtainPairView



class UserView(APIView):
    permission_classes = [permissions.AllowAny]
    # 사용자 정보 조회
    def get(self, request):
        print("1:", request.user)
        user_serializer = UserSerializer(request.user).data
        user_serializer['follower_n'] = UserFollowing.objects.filter(following_user_id=request.user.id).count() # 나를 팔로우 하는 사람 수
        user_serializer['following_n'] = UserFollowing.objects.filter(user_id=request.user.id).count() # 내가 팔로우 하는 사람 수
        print("2:", user_serializer)
        return Response(user_serializer, status=status.HTTP_200_OK)

    # 회원가입
    def post(self, request):
        user_serializer=UserSerializer(data=request.data)
        if user_serializer.is_valid():
            user_serializer.save()

            return Response(user_serializer.data, status=status.HTTP_200_OK)

# 로그인 기능
class TokenObtainPairView(TokenObtainPairView):
    serializer_class = TokenObtainPairSerializer


# 팔로잉
class UserFollowingView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def post(self,request):
        following_user=User.objects.get(username=request.data['username'])
        UserFollowing.objects.create(user_id=request.user, following_user_id= following_user)
        return Response({'msg:성공'}, status=status.HTTP_200_OK)

    #언팔로우
    def delete(self,request):
        following_user=User.objects.get(username=request.data['username'])
        UserFollowing.objects.filter(user_id=request.user, following_user_id=following_user).delete()
        return Response({'message': '삭제되었습니다'}, status=status.HTTP_200_OK)
