from rest_framework.views import APIView
from rest_framework import status, permissions
from rest_framework.response import Response

from .serializers_jwt import TokenObtainPairSerializer
from .serializers import UserProfileSerializer, UserSerializer, PetProfileSerializer

from .models import User, UserFollowing, PetProfile, UserProfile

from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken

from django.core.exceptions import ValidationError
from allauth.socialaccount.models import SocialAccount

# 회원가입
class UserView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        if request.user:
            user_serializer = UserSerializer(request.user).data
 
            user_serializer['followers'] = UserFollowing.objects.filter(following_user_id=request.user).count() # 나를 팔로우 하는 사람 수
            user_serializer['followings'] = UserFollowing.objects.filter(user_id=request.user).count() # 내가 팔로우 하는 사람 수
            return Response(user_serializer, status=status.HTTP_200_OK)
        return Response({"error": "접근 권한이 없습니다."}, status=status.HTTP_401_UNAUTHORIZED)


    def post(self, request):
        user_serializer=UserSerializer(data=request.data)

        if user_serializer.is_valid():
            user_serializer.save()
            return Response(user_serializer.data, status=status.HTTP_200_OK)
        return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# 로그인 기능
class TokenObtainPairView(TokenObtainPairView):
    serializer_class = TokenObtainPairSerializer


class KakaoLoginView(APIView):
    permission_classes = [permissions.AllowAny]
    def post(self, request):
        access_token = request.data['access_token']
        email = request.data['email']
        username = request.data['username']

        # {'access_token': 'DFOOTfzQtsNLr0AdCbuHR-mVMgIP3UsuB23KFSRpCj1y6gAAAYIOokiv', 'token_type': 'bearer', 'refresh_token': 'IAOdwEjWGviwfXRL-VA5mqv9zqRUYne3FaLQmu9fCj1y6gAAAYIOokiu', 'expires_in': 7199, 'scope': 'account_email gender profile_nickname', 'refresh_token_expires_in': 5183999, 'email': 'tulip_han@naver.com', 'username': '한예슬'}        
        try: 
            # 기존에 가입된 유저가 있다면 로그인
            user = User.objects.get(email=email)
            print(user.password)
            if user and (user.password==""):
                refresh = RefreshToken.for_user(user)

                return Response({'refresh': str(refresh), 'access': str(refresh.access_token), "msg" : "로그인 성공"}, status=status.HTTP_200_OK)
            elif user and (user.password!=""):
                return Response({"error": "해당 카카오 이메일을 사용해 일반 회원가입한 회원입니다"}, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
        #     # 기존에 가입된 유저가 없으면 새로 가입           
            new_user = User.objects.create(
                username=username,
                email=email,
            )
            new_user.save()
            return Response({"msg": "회원가입에 성공 했습니다."}, status=status.HTTP_201_CREATED)



# 수정
class OnlyAuthenticatedUserView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes=[JWTAuthentication]
    
    def get(self, request):
		# Token에서 인증된 user만 가져옴
        user = request.user
        if not user:
            return Response({"error": "접근 권한이 없습니다."}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(UserSerializer(request.user).data)
    
    def put(self, request, pk):
        user = User.objects.get(id=pk)
        if request.user != user:
            return Response({"error": "접근 권한이 없습니다."}, status=status.HTTP_401_UNAUTHORIZED)
        
        userprofile = UserProfile.objects.get(user=user)
        user_serializer = UserProfileSerializer(userprofile, data=request.data, partial=True)
        if user_serializer.is_valid():
            user_serializer.save()
            return Response(user_serializer.data, status=status.HTTP_200_OK)
        return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 팔로우/언팔로우
class UserFollowingView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes=[JWTAuthentication]

    def post(self,request):
        following_user=User.objects.get(username=request.data['username'])
        new_follow, created = UserFollowing.objects.get_or_create(user_id=request.user, following_user_id= following_user)
        if created:
            new_follow.save()
            return Response({"message": "팔로우 하셨습니다"}, status=status.HTTP_200_OK)
        new_follow.delete()
        return Response({"message":"팔로우 취소 하셨습니다"}, status=status.HTTP_200_OK)

class PetView(APIView):
    authentication_classes=[JWTAuthentication]

    def get(self, request):
        user = request.user
        pets = PetProfile.objects.filter(user=user)
        serializer = PetProfileSerializer(pets, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        user = request.user

        request.data['user'] = user.id

        print(request.data)
        serializer=PetProfileSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        pet = PetProfile.objects.get(pk=pk)
        serializer = PetProfileSerializer(pet, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        pet = PetProfile.objects.get(pk=pk)
        pet.delete()
        return Response({"massege" : "삭제 성공"},status=status.HTTP_200_OK)
