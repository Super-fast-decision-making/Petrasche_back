from rest_framework.views import APIView
from rest_framework import status, permissions
from rest_framework.response import Response

from .serializers_jwt import TokenObtainPairSerializer
from .serializers import UserSerializer

from rest_framework_simplejwt.views import TokenObtainPairView


#회원가입
class UserView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self,request):
        user_serializer=UserSerializer(data=request.data)
        if user_serializer.is_valid():
            user_serializer.save()
            # return Response({"msg:회원가입 성공"})
            return Response(user_serializer.data, status=status.HTTP_200_OK)

# 로그인 기능
class TokenObtainPairView(TokenObtainPairView):
    serializer_class = TokenObtainPairSerializer