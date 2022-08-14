from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from dateutil import parser


from .models import WalkingMate
from user.models import User
from .serializers import WalkingMateSerializer
# Create your views here.
from petrasche.pagination import PaginationHandlerMixin, BasePagination
from rest_framework_simplejwt.authentication import JWTAuthentication


class WalkingMateView(APIView, PaginationHandlerMixin):
    authentication_classes=[JWTAuthentication]
    pagination_class = BasePagination # query_param 설정 /?page=<int>
    serializer_class = WalkingMateSerializer
    def get(self,request):
        articles = WalkingMate.objects.all().order_by('-created_at')

        region = self.request.query_params.get('region','')
        gender = self.request.query_params.get('gender','')
        people_num = self.request.query_params.get('people_num','')
        size = self.request.query_params.get('size','')
        start_date = self.request.query_params.get('start_date','')

        param_keys=[region, gender, people_num, size, start_date]
        
        for key in param_keys:
            if key:
                articles = articles.filter(key=key)

        page = self.paginate_queryset(articles)
        if page != None:
            serializer = self.get_paginated_response(self.serializer_class(page, many=True).data)
        else:
            serializer = self.serializer_class(articles, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self,request):
        user= request.user
        request.data['host'] = user.id
        date=request.data['start_date']

        request.data['start_time']=date+' '+request.data['time'].split('~')[0]
        request.data['end_time']=date+' '+request.data['time'].split('~')[1]
        request.data['contents']=request.data['contents']#.strip('<p>').strip('</p>')
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

