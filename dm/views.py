from dm.models import Header
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from dm.serializers import HeaderSerializer
# Create your views here.
        
            
class HeaderView(APIView):
    authentication_classes=[JWTAuthentication]
    
    def get(self, request):
        user = request.user
        header = Header.objects.by_user(user=user.id).prefetch_related('header').order_by('-created_at')
        header_serializer = HeaderSerializer(header, many=True, context={'header':header}).data
        return Response(header_serializer, status=200)
    
    def post(self, request):
        header_serializer = HeaderSerializer(data=request.data)
        
        if header_serializer.is_valid():
            header_serializer.save()
            return Response(header_serializer.data, status=200)
        return Response(header_serializer.errors, status=400)
    
    
    
class ChatView(APIView):
    authentication_classes=[JWTAuthentication]
    
    def get(self, request, pk):
        header = Header.objects.filter(pk=pk)
        header_serializer = HeaderSerializer(header, many=True, context={'header':header}).data
        return Response(header_serializer, status=200)
                
        





















        
        
    
        