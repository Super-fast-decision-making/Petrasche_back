from asyncore import write
from numpy import require
from rest_framework import serializers
from article.models import Article, Image, Comment

class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = '__all__'

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = '__all__'

class ArticleSerializer(serializers.ModelSerializer):
    comment = CommentSerializer(many=True, read_only=True, source='comment_set')
    image_list = serializers.SerializerMethodField()
    images = serializers.ListField(write_only=True, required=False)

    def get_image_list(self, obj):
        imgurls = []
        for image in obj.image_set.all():
            imgurls.append(image.imgurl)
        return imgurls

    # 여기서 계속 에러 나서 일단 주석처리
    # View.py 일단 구현
    # def create(self, validated_data):
    #     images = validated_data.pop('images')
        # article = Article(**validated_data)
        # article.save()
    #     # for image in images:
    #     #     image_data = {'article': article, 'imgurl': image}
    #     #     Image.objects.create(**image_data)
        # return article

    def update(self, instance, validated_data):
        images = validated_data.pop('images')
        instance.title = validated_data.get('title', instance.title)
        instance.content = validated_data.get('content', instance.content)
        instance.is_active = validated_data.get('is_active', instance.is_active)
        instance.save()
        return instance

    class Meta:
        model = Article
        fields = '__all__'