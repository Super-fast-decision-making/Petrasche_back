from asyncore import write
from rest_framework import serializers
from article.models import Article, Image, Comment
from article.s3upload import upload as s3
from datetime import datetime

class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = '__all__'

class CommentSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField()
    date = serializers.SerializerMethodField()
    
    def get_username(self, obj):
        if obj.user:
            return obj.user.username
        return "삭제된 사용자"

    def get_date(self, obj):
        time = datetime.now()
        if (obj.created_at.date()==time.date()) and (obj.created_at.hour==time.hour):
            return str(time.minute-obj.created_at.minute)+"분전"
        elif obj.created_at.date()==time.date():
            return str(time.hour-obj.created_at.hour)+"시간전"
        elif obj.created_at.month==time.month:
            return  str(time.day-obj.created_at.day) + "일전"
        elif obj.created_at.year ==time.year:
            return str(time.month-obj.created_at.month) + "달전"
        else:
            return obj.created_at

    class Meta:
        model = Comment
        fields = '__all__'

class ArticleSerializer(serializers.ModelSerializer):
    comment = CommentSerializer(many=True, read_only=True, source='comment_set')
    likes = serializers.SerializerMethodField()
    like_num = serializers.SerializerMethodField()
    images = serializers.SerializerMethodField()
    image_lists = serializers.ListField(write_only=True, required=False)
    author = serializers.SerializerMethodField()
    date = serializers.SerializerMethodField()


    def get_author(self,obj):
        return obj.user.username

    def get_likes(self, obj):
        return [like.username for like in obj.like.all()]

    def get_like_num(self,obj):
        return  obj.like.all().count()

    def get_images(self, obj):
        return [image.imgurl for image in obj.image_set.all()]

    def get_date(self, obj):
        time = datetime.now()
        if (obj.created_at.date()==time.date()) and (obj.created_at.hour==time.hour):
            return str(time.minute-obj.created_at.minute)+"분전 "
        elif obj.created_at.date()==time.date():
            return str(time.hour-obj.created_at.hour)+"시간전"
        elif obj.created_at.month==time.month:
            return  str(time.day-obj.created_at.day) + "일전"
        elif obj.created_at.year ==time.year:
            return str(time.month-obj.created_at.month) + "달전"
        else:
            return obj.created_at

    def create(self, validated_data):
        image_lists = validated_data.pop('image_lists')
        user = validated_data['user']
        user = user.id
        imgurls = []
        for image in image_lists:
            url = s3(user, image)
            imgurls.append(url)
        article = Article(**validated_data)
        article.save()
        for imageurl in imgurls:
            image_data = {'article': article, 'imgurl': imageurl}
            Image.objects.create(**image_data)
        return article

    def update(self, instance, validated_data):
        instance.title = validated_data.get('title', instance.title)
        instance.content = validated_data.get('content', instance.content)
        instance.is_active = validated_data.get('is_active', instance.is_active)
        instance.save()
        return instance

    class Meta:
        model = Article
        fields = ['id', 'user', 'title', 'content', 'is_active', 'comment', 'images', 'image_lists', 'likes', 'like_num', 'author', 'date']


# class  LikeSerailzier(serializers.ModelSerializer):
#     articles = ArticleSerializer(many=True, read_only=True, source='article_set')
#     class Meta:
#         model = Like
#         fields = '__all__'