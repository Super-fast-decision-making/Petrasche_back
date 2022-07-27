from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from dateutil import parser


from .models import WalkingMate
from user.models import User
from .serializers import WalkingMateSerializer
# Create your views here.




class WalkingMateView(APIView):
    def get(self,request):
        check_region = self.request.query_params.get('region','')
        check_gender = self.request.query_params.get('gender','')
        check_number = self.request.query_params.get('people_num','')
        check_size = self.request.query_params.get('size','')

        articles = WalkingMate.objects.all().order_by('-created_at')
        if check_gender:
            articles= articles.filter(gender=check_gender)

        if check_region:
            articles= articles.filter(region=check_region)

        if check_number:
            articles= articles.filter(people_num=check_number)

        if check_size:
            articles= articles.filter(size=check_size)


        serializer = WalkingMateSerializer(articles, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self,request):
        user= request.user
        request.data['host'] = user.id
        date=request.data['start_date']

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
        article = WalkingMate.objects.get(pk=pk)
        serializer = WalkingMateSerializer(article).data

        if request.user.id in serializer['attending_user']:
            serializer['attending'] = True
        else:
            serializer['attending'] = False
        return Response(serializer, status=status.HTTP_200_OK)

    # 여기서 put 메소드는 산책 모임 참여자 추가
    # def put(self, request, pk):
        
    #     article = WalkingMate.objects.get(pk=pk)
        
        
    #     article.attending_user.add(request.user.id)
        
    #     return Response({"message" : "추가 성공"}, status=status.HTTP_200_OK)

    def delete(self, request, pk):
        article = WalkingMate.objects.get(pk=pk)
        article.delete()
        return Response({"message" : "삭제 성공"},status=status.HTTP_200_OK)
    

#산책 모임 참여자 추가/삭제
class WalkingMateAttenderView(APIView):
    def post (self, request,pk):
        article = WalkingMate.objects.get(pk=pk)
        article.attending_user.add(request.user.id)
        return Response({"message" : "추가 성공"}, status=status.HTTP_200_OK)

    def delete(self, request, pk):
        article = WalkingMate.objects.get(pk=pk)
        article.attending_user.remove(request.user.id)
        return Response({"message" : "삭제 성공"},status=status.HTTP_200_OK)

