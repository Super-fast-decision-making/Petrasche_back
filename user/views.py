from itertools import chain
from rest_framework.views import APIView
from rest_framework import status, permissions
from rest_framework.response import Response

from .serializers_jwt import TokenObtainPairSerializer
from .serializers import UserProfileSerializer, UserSerializer, PetProfileSerializer

from .models import User, UserFollowing, PetProfile, UserProfile
from article.models import Article, Comment

from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken

from django.core.exceptions import ValidationError
from datetime import datetime, timedelta

from django.contrib.auth.hashers import check_password


def time_calculate(time):
    if time < 60:
        time = str(time) + '초전'
    elif time < 3600:
        time = str(int(time / 60)) + '분전'
    elif time < 86400:
        time = str(int(time / 3600)) + '시간전'
    elif time < 604800:
        time = str(int(time / 86400)) + '일전'
    elif time < 2592000:
        time = str(int(time / 604800)) + '주전'
    elif time < 31536000:
        time = str(int(time / 2592000)) + '달전'
    else:
        time = str(int(time / 31536000)) + '년전' 
    
    return time

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
        email = request.data['email']
        username = request.data['username']
        try: 
            # 기존에 가입된 유저가 있다면 로그인
            user = User.objects.get(email=email)
            if user and (user.password==None):
                refresh = RefreshToken.for_user(user)

                return Response({'refresh': str(refresh), 'access': str(refresh.access_token), "msg" : "로그인 성공"}, status=status.HTTP_200_OK)
            elif user and (user.password!=None):
                return Response({"error": "해당 카카오 이메일을 사용해 일반 회원가입한 회원입니다"}, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
        # 기존에 가입된 유저가 없으면 새로 가입           
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
        
        for key, value in request.data.items():
            if key == "password":
                if check_password(value,user.password):
                    return Response({"massege" : "이전과 같은 비밀번호는 사용할 수 없습니다."}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    user_serializer = UserSerializer(user, data=request.data, partial=True)
            else:
                userprofile = UserProfile.objects.get(user=user)
                user_serializer = UserProfileSerializer(userprofile, data=request.data, partial=True)

        if user_serializer.is_valid():
            user_serializer.save()
            return Response({"massege" : "변경되었습니다.", "response": user_serializer.data}, status=status.HTTP_200_OK)
        return Response({"massege" : "변경 오류", "response": user_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


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

        serializer=PetProfileSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PetDetailView(APIView):
    authentication_classes=[JWTAuthentication]

    def get(self, request,pk):
        pet = PetProfile.objects.get(id=pk)
        print(pet)
        return Response(PetProfileSerializer(pet).data, status=status.HTTP_200_OK)

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
        return Response({"massege" : "프로필이 삭제되었습니다."},status=status.HTTP_200_OK)

class HistoryView(APIView):
    authentication_classes=[JWTAuthentication]

    def get(self, request):
        user = request.user
        following = UserFollowing.objects.filter(following_user_id=user)[:10]
        histories = Article.objects.filter(user=user).order_by('-created_at')[:10]
        histories_comments = Comment.objects.filter(article__user=user).order_by('-created_at')[:10]
        histories = list(chain(histories, histories_comments, following))
        histories.sort(key=lambda x: x.created_at, reverse=True)
        histories = histories[:15]
        history_list = []
        for history in histories:
            try:
                for like in history.like.all():
                    if like.username == user.username:
                        pass
                    else:
                        time = (datetime.now() - history.created_at).total_seconds()
                        time = time_calculate(time)
                        
                        doc = {
                            "content": history.content,
                            "user": like.username,
                            "time" : time,
                            "type" : "like",
                        }
                        history_list.append(doc)
            except AttributeError:
                try:
                    if history.user == user:
                        pass
                    else:
                        time = (datetime.now() - history.created_at).total_seconds()
                        time = time_calculate(time)

                        doc = {
                            "content": "None",
                            "user": history.user.username,
                            "time" : time,
                            "type" : "comment",
                        }
                        history_list.append(doc)
                except:
                    time = (datetime.now() - history.created_at).total_seconds()
                    time = int(time)
                    time = time_calculate(time)

                    doc = {
                        "content" : "None",
                        "user" : history.user_id.username,
                        "time" : time,
                        "type" : "follow",
                    }
                    history_list.append(doc)

        return Response(history_list, status=status.HTTP_200_OK)
# 비밀번호 인증

class AuthPasswordView(APIView):

    def post(self, request):
        origin_password = request.user.password
        input_password = request.data['password']

        if check_password(input_password,origin_password):
            return Response({"massege" : "인증되었습니다.", "response": request.user.id}, status=status.HTTP_200_OK)
        return Response({"massege" : "비밀번호가 일치하지 않습니다."}, status=status.HTTP_400_BAD_REQUEST)