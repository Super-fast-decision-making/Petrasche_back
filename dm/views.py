from django.shortcuts import render, get_object_or_404

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import status, permissions
from rest_framework.generics import CreateAPIView, ListAPIView

from dm.models import Message, Channel
from dm.serializers import ChannelSerializer, MessageCreateSerializer, MessageListSerializer

from datetime import datetime
# Create your views here.


class ChannelCreateAPIView(CreateAPIView):
    serializer_class = ChannelSerializer
    # permission_classes = [permissions.IsAuthenticated]
    authentication_classes=[JWTAuthentication]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class ChannelListAPIView(ListAPIView):
    serializer_class = ChannelSerializer
    queryset = Channel.objects.all()


class MessageCreateView(APIView):
    serializer_class = MessageCreateSerializer

    def post(self, request, channel_id):
        my_data = request.data
        serializer = self.serializer_class(data=my_data)
        if serializer.is_valid():
            valid_data = serializer.data
            new_data = {
                'message': valid_data['message'],
                'user': request.user,
                'channel': Channel.objects.get(id=channel_id)
            }
            new_message = Message.objects.create(**new_data)
            return Response({
                'message': valid_data['message'],
                'username': request.user.username,
                'timestamp': new_message.timestamp
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MessageListView(APIView):

    def get(self, request, channel_id):
        print(request.user.username)
        print(datetime.now())
        print(channel_id)
        messages = Message.objects.filter(
            channel=Channel.objects.get(id=channel_id))
        latest = request.GET.get('latest')
        if latest:
            messages = messages.filter(timestamp__gt=latest)

        message_list = MessageListSerializer(messages, many=True).data

        return Response(message_list, status=status.HTTP_200_OK)
























# class MessagelistView(APIView):
    
#     def get(self, request, sender=None, receiver=None):
#         # messages = Message.objects.all()
#         messages = Message.objects.filter(sender=sender, receiver=receiver, seen=False)
#         message_serializer = MessageSerializer(messages, many=True, context={'request':request})
#         for message in messages:
#             message.seen = True
#             message.save()
#         return Response(message_serializer.data)
    
#     def post(self, request, sender=None, receiver=None):
#         data = JSONParser().parse(request)
#         serializer = MessageSerializer(data=data)
#         if serializer.is_valid():
#             serializer.save()
#             return JsonResponse(serializer.data, status=201)
#         return JsonResponse(serializer.errors, status=400)
        
        
    
        