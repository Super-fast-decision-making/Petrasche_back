from django.dispatch import receiver
from dm.models import Header, Message
from user.models import User
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from dm.serializers import HeaderSerializer, MessageSerializer
# Create your views here.
        
            
class HeaderView(APIView):
    def get(self, request):
        header = Header.objects.by_user(user=request.user).prefetch_related('header').order_by('-created_at')
        header_serializer = HeaderSerializer(header, many=True, context={'header':header}).data
        return Response(header_serializer, status=200)





















        
        
    
        