from dm.models import Header
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from dm.serializers import HeaderSerializer
# Create your views here.
        
            
class HeaderView(APIView):
    authentication_classes=[JWTAuthentication]
    
    def get(self, request):
        header = Header.objects.by_user(user=request.user).prefetch_related('header').order_by('-created_at')
        header_serializer = HeaderSerializer(header, many=True, context={'header':header}).data
        return Response(header_serializer, status=200)





















        
        
    
        