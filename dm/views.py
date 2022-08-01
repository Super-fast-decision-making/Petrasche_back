from django.dispatch import receiver
from dm import serializers
from dm.models import Header
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from dm.serializers import HeaderSerializer, UserHeaderSerializer
from user.models import User
# Create your views here.
        
class HeaderView(APIView):
    authentication_classes=[JWTAuthentication]
    
    # 활성화된 채팅방 리스트
    def get(self, request):
        user = request.user
        header = Header.objects.by_user(user=user.id).prefetch_related('header').order_by('-created_at')
        header_serializer = HeaderSerializer(header, many=True, context={'header':header}).data
        return Response(header_serializer, status=200)
    

class ChatView(APIView):
    authentication_classes=[JWTAuthentication]
    
    # 해당 채티방(pk=pk)의 메시지 리스트
    def get(self, request, pk):
        header = Header.objects.filter(pk=pk)
        header_serializer = HeaderSerializer(header, many=True, context={'header':header}).data
        return Response(header_serializer, status=200)

    # receiver(pk=pk) 채팅방 생성
    def post(self, request, pk):
        sender = request.user
        receiver = User.objects.get(pk=pk)       
        try:
            #존재하는 채팅방이 있다면, 채팅방을 가져온다.
            header = Header.objects.get(sender=sender.id, receiver=receiver.id)
            header_serializer = HeaderSerializer(header).data
            return Response(header_serializer, status=200)
        except Header.DoesNotExist:
            #존재하는 채팅방이 없다면, 새롭게 생성
            Header.objects.create(
                sender=sender, 
                receiver=receiver, 
            )
            return Response({"msg": "채팅방 생성!"}, status=200)
        
        
class UserHeaderView(APIView):
    authentication_classes=[JWTAuthentication]
    # 활성화된 채팅방 리스트
    def get(self, request, pk):
        user = request.user
        user = User.objects.filter(id=pk)
        serializer = UserHeaderSerializer(user, many=True)
        return Response(serializer.data, status=200)
                
