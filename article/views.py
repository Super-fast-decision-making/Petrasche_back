import re
from elasticsearch import Elasticsearch
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from article.models import Article, Image, Comment
from article.serializers import ArticleSerializer, ImageSerializer, CommentSerializer
from django.db.models import Count
from user.models import User,PetProfile

from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import status, permissions
import requests

from petrasche.settings import es_url

from petrasche.pagination import PaginationHandlerMixin, BasePagination

from article.s3upload import delete as s3_delete

from article.replacehtml import replace_html as text_re

class ArticleView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        articles = Article.objects.all().order_by('-created_at')[:20]
        serializer = ArticleSerializer(articles, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


    def post(self, request):
        user = request.user
        request.data['user'] = user.id
        serializer = ArticleSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ArticleTopView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        articles = Article.objects.all()
        top_articles = articles.annotate(like_count=Count('like')).annotate(comment_count=Count('comment')).order_by('-like_count')[:9]
        top_articles = ArticleSerializer(top_articles, many=True)
        return Response(top_articles.data, status=status.HTTP_200_OK)

class ArticleDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes=[JWTAuthentication]

    def get(self, request, pk):
        article = Article.objects.get(pk=pk)
        serializer = ArticleSerializer(article)
        return Response(serializer.data, status=status.HTTP_200_OK)

class CommentView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes=[JWTAuthentication]

    def get(self, request, pk):
        comments = Comment.objects.filter(article=pk).order_by('-id')
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
        
    def post(self, request, pk):
        user = request.user
        article = Article.objects.get(pk=pk)
        request.data['article'] = article.id
        request.data['user'] = user.id
        request.data['comment'] = text_re(request.data['comment'])
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        user = request.user
        comment = Comment.objects.get(pk=pk)
        request.data['comment'] = text_re(request.data['comment'])
        if comment.user == user:
            serializer = CommentSerializer(comment, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({"massege" : "수정 권한이 없습니다."},status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk):
        user = request.user
        comment = Comment.objects.get(pk=pk)
        if comment.user == user:
            comment.delete()
            return Response({"massege" : "삭제"},status=status.HTTP_200_OK)
        return Response({"massege" : "삭제 권한이 없습니다."},status=status.HTTP_400_BAD_REQUEST)

class LikeView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes=[JWTAuthentication]

    def post(self, request, pk):
        user = request.user
        try: 
            article = Article.objects.get(pk=pk)
        except:
            return Response({"massege" : "존재하지 않는 게시물입니다."},status=status.HTTP_400_BAD_REQUEST)
        if user in article.like.all():
            article.like.remove(user)
            return Response({"massege" : "좋아요 취소"},status=status.HTTP_200_OK)
        else:
            article.like.add(user)
            return Response({"massege" : "좋아요"},status=status.HTTP_200_OK)

class MyArticleView(APIView, PaginationHandlerMixin):

    authentication_classes=[JWTAuthentication]
    pagination_class = BasePagination # query_param 설정 /?page=<int>
    serializer_class = ArticleSerializer

    def get(self, request):
        user = request.user
        articles = Article.objects.filter(user=user).order_by('-id')
        page = self.paginate_queryset(articles)
        if page != None:
            serializer = self.get_paginated_response(self.serializer_class(page, many=True).data)
        else:
            serializer = self.serializer_class(articles, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

        

    def put(self, request, pk):
        user = request.user
        request.data['content'] = text_re(request.data['content'])
        article = Article.objects.get(pk=pk)
        if article.user == user:
            serializer = ArticleSerializer(article, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({"massege" : "수정 권한이 없습니다."},status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        user = request.user
        article = Article.objects.get(pk=pk)
        if article.user == user:
            for image in article.image_set.all():
                image_file = image.imgurl.replace('https://pracs3.s3.ap-northeast-2.amazonaws.com/', '')
                s3_delete(image_file)
            article.delete()
            
            requests.delete(es_url + f"/article/{pk}") # es delete
            requests.delete(es_url + f"/hashtag/{pk}") # es hashtag delete
            
            return Response({"massege" : "삭제 성공"},status=status.HTTP_200_OK)
        return Response({"massege" : "삭제 권한이 없습니다."},status=status.HTTP_400_BAD_REQUEST)
    
    
# es _search
class SearchView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes=[JWTAuthentication]

    def get(self, request):
        search_words = request.query_params.get('words', '').strip()
        if search_words == '' or not search_words:
            return Response({'message': '검색어를 입력해 주세요.'}, status=status.HTTP_404_NOT_FOUND)
        
        if search_words.startswith('#'):
            pattern = '#([0-9a-zA-Z가-힣]*)'
            hash_w = re.compile(pattern)

            hashtags = hash_w.findall(search_words)
            res = requests.get(es_url+'/hashtag/_search?q='+ hashtags[0])
        else:
            res = requests.get(es_url+'/article/_search?q='+ search_words)
        response = res.json()
        article_pk_list = []
        try:
            for obj in response['hits']['hits']:
                article_pk_list.append(obj["_source"]["pk"])
            articles = Article.objects.filter(pk__in=article_pk_list)
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'message': '검색 결과가 없습니다.'})
        return Response(ArticleSerializer(articles, many=True).data, status=status.HTTP_200_OK)


class HashTagSearchView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes=[JWTAuthentication]

    def get(self, request):
        search_words = request.query_params.get('words', '').strip()
        if search_words == '' or not search_words:
            return Response(data={'message': '검색 결과가 없습니다.'}, status=status.HTTP_400_BAD_REQUEST)
        
        res = requests.get(es_url+'/hashtag/_search?q='+ search_words)
        response = res.json()
        article_pk_list = []
        try:
            for obj in response['hits']['hits']:
                article_pk_list.append(obj["_source"]["pk"])
            articles = Article.objects.filter(pk__in=article_pk_list)
        except:
            return Response(data={'message': '검색 결과가 없습니다.'}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(ArticleSerializer(articles, many=True).data, status=status.HTTP_200_OK)



class ArticleScrollView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes=[JWTAuthentication]

    def get(self, request, page):
        start = (int(page))*20 + 1
        end = start + 20
        articles = Article.objects.all().order_by('-created_at')[start:end]
        serializer = ArticleSerializer(articles, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class ArticleSelectView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes=[JWTAuthentication]

    def get(self, request, pet):
        petprofiles = PetProfile.objects.filter(type=pet)
        articles = Article.objects.filter(petprofile__in=petprofiles).order_by('-created_at')
        serializer = ArticleSerializer(articles, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
            


