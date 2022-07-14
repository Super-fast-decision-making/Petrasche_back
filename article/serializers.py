from asyncore import write
from rest_framework import serializers
from article.models import Article, Image, Comment
from article.s3upload import upload as s3

class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = '__all__'

class CommentSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    def get_user(self, obj):
        try:
            return obj.user.username
        except:
            return f'없음'

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

    def get_author(self,obj):
        return obj.user.username

    def get_likes(self, obj):
        return [like.username for like in obj.like.all()]

    def get_like_num(self,obj):
        return  obj.like.all().count()

    def get_images(self, obj):
        return [image.imgurl for image in obj.image_set.all()]

    def create(self, validated_data):
        image_lists = validated_data.pop('image_lists')
        user = validated_data['user']
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
        fields = ['id', 'user', 'title', 'content', 'is_active', 'comment', 'images', 'image_lists', 'likes', 'like_num', 'author']


# class  LikeSerailzier(serializers.ModelSerializer):
#     articles = ArticleSerializer(many=True, read_only=True, source='article_set')
#     class Meta:
#         model = Like
#         fields = '__all__'