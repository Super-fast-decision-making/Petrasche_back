from asyncore import write
import re
from rest_framework import serializers
from article.models import Article, Image, Comment
from article.s3upload import upload as s3
from datetime import datetime
from user.models import UserFollowing, PetProfile, UserProfile
from dm.serializers import BaseSerializer
from user.models import UserFollowing
import requests

es_url = 'http://localhost:9200'
# es_url = 'http://15.164.171.221:9200/'

class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = '__all__'


class CommentSerializer(BaseSerializer):
    username = serializers.SerializerMethodField()
    
    def get_username(self, obj):
        if obj.user:
            return obj.user.username
        return "삭제된 사용자"
    class Meta:
        model = Comment
        fields = '__all__'


class ArticleSerializer(BaseSerializer):
    article_pet_list = serializers.SerializerMethodField()
    comment = CommentSerializer(many=True, read_only=True, source='comment_set')
    likes = serializers.SerializerMethodField()
    like_users = serializers.SerializerMethodField()
    like_num = serializers.SerializerMethodField()
    images = serializers.SerializerMethodField()
    image_lists = serializers.ListField(write_only=True, required=False)
    user_pet = serializers.IntegerField(write_only=True, required=False)
    author = serializers.SerializerMethodField()
    user_following = serializers.SerializerMethodField()
    profile_img = serializers.SerializerMethodField()

    def get_profile_img(self, obj):
        user_profiles = UserProfile.objects.filter(user=obj.user.id)
        return [user_profile.profile_img for user_profile in user_profiles]

    def get_user_following(self, obj):
        users = UserFollowing.objects.filter(following_user_id=obj.user.id)
        return [user.user_id.id for user in users]

    def get_article_pet_list(self, obj):
        return [pet.id for pet in obj.petprofile_set.all()]
        
    def get_author(self,obj):
        return obj.user.username

    def get_likes(self, obj):
        return [like.id for like in obj.like.all()]

    def get_like_users(self, obj):
        return [like.username for like in obj.like.all()]

    def get_like_num(self,obj):
        return  obj.like.all().count()

    def get_images(self, obj):
        return [image.imgurl for image in obj.image_set.all()]

    def create(self, validated_data):
        try:
            user_pet = validated_data.pop('user_pet')
        except:
            pass
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
        # es indexing 
        es_body = {
            "pk": article.pk,
            "title": article.title,
            "content": article.content
        }
        requests.post(es_url+f"/article/_doc/{article.pk}", json=es_body)
        
        # hashtags
        pattern = '#([0-9a-zA-Z가-힣]*)'
        hash_w = re.compile(pattern)

        hashtags = hash_w.findall(article.content)
        print("해시태그 추출: ", hashtags)
        es_hashtags_input = ""
        for tag in hashtags:
            print("tag => ", tag)
            es_hashtags_input += " "+tag
            
        es_hashtag_body = {
            "pk": article.pk,
            "hashtags": es_hashtags_input
        }
        requests.post(es_url+f"/hashtag/_doc/{article.pk}", json=es_hashtag_body)

        
        try:
            pet = PetProfile.objects.get(id=user_pet)
            pet.article.add(article)
            pet.save()
        except:
            pass
        return article

    def update(self, instance, validated_data):
        instance.title = validated_data.get('title', instance.title)
        instance.content = validated_data.get('content', instance.content)
        instance.is_active = validated_data.get('is_active', instance.is_active)
        instance.save()


        # es update
        es_body = {
            "doc": {
                "title": instance.title,
                "content": instance.content
            }
        }
        requests.post(es_url+f"/article/_update/{instance.pk}", json=es_body)

        
        # es hashtag update
        pattern = '#([0-9a-zA-Z가-힣]*)'
        hash_w = re.compile(pattern)

        hashtags = hash_w.findall(instance.content)
        print("해시태그 추출: ", hashtags)
        es_hashtags_input = ""
        for tag in hashtags:
            print("tag => ", tag)
            es_hashtags_input += " "+tag
        
        es_hashtag_body = {
            "doc": {
                "hashtags": es_hashtags_input
            }
        }
        requests.post(es_url+f"/hashtag/_update/{instance.pk}", json=es_hashtag_body)

        return instance

    class Meta:
        model = Article
        fields = ['id', 'user', 'title', 'content', 'is_active', 'comment', 'images', 'image_lists', 'likes', 'like_num', 'author', 'date', 'user_following','user_pet','article_pet_list','like_users', 'profile_img']
