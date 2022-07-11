from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from article.models import Article, Image, Comment
from article.serializers import ArticleSerializer, ImageSerializer, CommentSerializer
from user.models import User

from rest_framework_simplejwt.authentication import JWTAuthentication


class ArticleView(APIView):
    def get(self, request):
        articles = Article.objects.all()
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

class MyArticleView(APIView):

    authentication_classes=[JWTAuthentication]

    def get(self, request):
        user = request.user
        articles = Article.objects.filter(user=user)
        serializer = ArticleSerializer(articles, many=True)
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
        return Response({"massege" : "삭제 성공"},status=status.HTTP_200_OK)