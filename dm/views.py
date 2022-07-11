from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.contrib.humanize.templatetags.humanize import naturaltime
from django.http.response import JsonResponse

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import JSONParser

from django.db.models import Q
from user.models import User
from dm.models import Message 
from dm.serializers import MessageSerializer

# Create your views here.

class MessageView(APIView):
    def get(self, request, sender=None, receiver=None):
        messages = Message.objects.filter(sender=sender, receiver=receiver, seen=False)
        message_serializer = MessageSerializer(messages, many=True, context={'request':request})
        for message in messages:
            message.seen = True
            message.save()
        return Response(message_serializer.data)
    
    def post(self, request, sender=None, receiver=None):
        data = JSONParser().parse(request)
        serializer = MessageSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=201)
        return JsonResponse(serializer.errors, status=400)
        
        