from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


from .models import WalkingMate
from .serializers import WalkingMateSerializer
# Create your views here.




class WalkingMateView(APIView):
    def get(self,request):
        articles = WalkingMate.objects.all().order_by('-created_at')
        serializer = WalkingMateSerializer(articles, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self,request):
        user= request.user
        print(user)
        request.data['host'] = user.id
        serializer = WalkingMateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


class WalkingMateDetailView(APIView):

    #     
    def put(self, request, pk):
        article = WalkingMate.objects.get(pk=pk)
        serializer = WalkingMateSerializer(article, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        article = WalkingMate.objects.get(pk=pk)
        article.delete()
        return Response({"massege" : "삭제 성공"},status=status.HTTP_200_OK)

    


