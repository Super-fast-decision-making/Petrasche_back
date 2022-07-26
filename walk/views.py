from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from dateutil import parser


from .models import WalkingMate
from .serializers import WalkingMateSerializer
# Create your views here.




class WalkingMateView(APIView):
    def get(self,request):
        check_regions = self.request.query_params.get('region','')
        check_gender = self.request.query_params.get('gender','')
        check_number = self.request.query_params.get('people_num','')
        check_size = self.request.query_params.get('size','')
        if check_regions:
            articles=WalkingMate.objects.filter(region=check_regions)
        elif check_gender:
            articles=WalkingMate.objects.filter(gender=check_gender)
        elif check_number:
            articles=WalkingMate.objects.filter(people_num=check_number)
        elif check_size:
            articles=WalkingMate.objects.filter(size=check_size)
        else:
            articles = WalkingMate.objects.all().order_by('-created_at')
        serializer = WalkingMateSerializer(articles, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self,request):
        user= request.user
        request.data['host'] = user.id
        d=request.data['date'].replace(' ','').split('.')
        date=d[0]+'-'+d[1]+'-'+d[2]
        request.data['start_time']=date+' '+request.data['time'].split('~')[0]
        request.data['end_time']=date+' '+request.data['time'].split('~')[1]
        request.data['contents']=request.data['contents'].strip('<p>').strip('</p>')
        serializer = WalkingMateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


class WalkingMateDetailView(APIView):

    def get(self, request, pk):
        

        articles = WalkingMate.objects.get(pk=pk)
        serializer = WalkingMateSerializer(articles, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

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

    


