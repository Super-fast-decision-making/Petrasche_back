import re
from elasticsearch import Elasticsearch
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from article.models import Article, Image, Comment
from article.serializers import ArticleSerializer, ImageSerializer, CommentSerializer
from django.db.models import Count
from user.models import User

from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import status, permissions
import requests


# es_url = 'http://allenpoe.iptime.org:9200/'
# es_url = 'http://15.164.171.221:9200/'

from petrasche.settings import es_url

from petrasche.pagination import PaginationHandlerMixin, BasePagination

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
    def get(self, request):
        articles = Article.objects.all()
        top_articles = articles.annotate(like_count=Count('like')).annotate(comment_count=Count('comment')).order_by('-like_count')[:7]
        top_articles = ArticleSerializer(top_articles, many=True)
        return Response(top_articles.data, status=status.HTTP_200_OK)

class ArticleDetailView(APIView):
    def get(self, request, pk):
        article = Article.objects.get(pk=pk)
        serializer = ArticleSerializer(article)
        return Response(serializer.data, status=status.HTTP_200_OK)

class CommentView(APIView):
    def get(self, request, pk):
        comments = Comment.objects.filter(article=pk)
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
        
    def post(self, request, pk):
        user = request.user
        article = Article.objects.get(pk=pk)
        request.data['article'] = article.id
        request.data['user'] = user.id
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        comment = Comment.objects.get(pk=pk)
        serializer = CommentSerializer(comment, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk):
        comment = Comment.objects.get(pk=pk)
        comment.delete()
        return Response({"massege" : "삭제 성공"},status=status.HTTP_200_OK)

class LikeView(APIView):
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
        article = Article.objects.get(pk=pk)
        serializer = ArticleSerializer(article, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        article = Article.objects.get(pk=pk)
        article.delete()
        
        requests.delete(es_url + f"/article/{pk}") # es delete
        requests.delete(es_url + f"/hashtag/{pk}") # es hashtag delete
        
        return Response({"massege" : "삭제 성공"},status=status.HTTP_200_OK)
    
    
# es _search
class SearchView(APIView):

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
    authentication_classes=[JWTAuthentication]

    def get(self, request,page):
        start = (int(page))*20
        end = start + 20
        articles = Article.objects.all().order_by('created_at')[start:end]
        serializer = ArticleSerializer(articles, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
