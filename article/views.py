from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from article.models import Article, Image, Comment
from article.serializers import ArticleSerializer, ImageSerializer, CommentSerializer
import datetime
from article.s3upload import upload as s3
from user.models import User

class ArticleView(APIView):
    def get(self, request):
        articles = Article.objects.all()
        serializer = ArticleSerializer(articles, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        user = request.user
        user = user.id
        request.data['user'] = user
        images = request.FILES.getlist('image_lists')
        imgurls = []
        for image in images:
            url = s3(user, image)
            imgurls.append(url)
        serializer = ArticleSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            for imgurl in imgurls:
                Image.objects.create(article=serializer.instance, imgurl=imgurl)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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

class CommentView(APIView):
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