from asyncore import write
from rest_framework import serializers
from article.models import Article, Image, Comment
from article.s3upload import upload as s3

class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = '__all__'

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = '__all__'

class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = '__all__'

class ArticleSerializer(serializers.ModelSerializer):
    comment = CommentSerializer(many=True, read_only=True, source='comment_set')
    image_list = serializers.SerializerMethodField()
    image_lists = serializers.ListField(write_only=True, required=False)

    def get_image_list(self, obj):
        imgurls = []
        for image in obj.image_set.all():
            imgurls.append(image.imgurl)
        return imgurls

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
        images = validated_data.pop('images')
        instance.title = validated_data.get('title', instance.title)
        instance.content = validated_data.get('content', instance.content)
        instance.is_active = validated_data.get('is_active', instance.is_active)
        instance.save()
        return instance

    class Meta:
        model = Article
        fields = ['id', 'user', 'title', 'content', 'is_active', 'comment', 'image_list', 'image_lists']