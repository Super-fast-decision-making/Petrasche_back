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
        check_region = self.request.query_params.get('region','')
        check_gender = self.request.query_params.get('gender','')
        check_number = self.request.query_params.get('number','')
        check_size = self.request.query_params.get('size','')
        check_date = self.request.query_params.get('start_date','')

        articles = WalkingMate.objects.all().order_by('-created_at')
        if check_date:
            articles= articles.filter(start_date=check_date)
        if check_gender:
            articles= articles.filter(gender=check_gender)
        if check_region:
            articles= articles.filter(region=check_region)
        if check_number:
            articles= articles.filter(people_num=check_number)
        if check_size:
            articles= articles.filter(size=check_size)

        page = self.paginate_queryset(articles)
        if page != None:

            serializer = self.get_paginated_response(self.serializer_class(page, many=True).data)
        else:
            serializer = self.serializer_class(articles, many=True)
        # print(serializer.data)
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

