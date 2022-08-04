from copy import deepcopy
from rest_framework import serializers
from .models import User, PetProfile, UserProfile
from article.models import Article, Image, Comment
from article.serializers import ArticleSerializer
from user.s3upload import upload as s3
from user.mr import image_type as mr

EMAIL = ("@naver.com", "@gmail.com", "@kakao.com")

class PetProfileSerializer(serializers.ModelSerializer):

    # pet_owner = serializers.SerializerMethodField()
    article = ArticleSerializer(many=True, read_only=True)
    image_file = serializers.FileField(write_only=True)

    # def get_pet_owner(self, obj):
    #     return obj.user.username

    def create(self, validated_data):
        name = validated_data.pop('name')
        birthday = validated_data.pop('birthday')
        gender = validated_data.pop('gender')
        size = validated_data.pop('size')
        user = validated_data.pop('user')
        image_file = validated_data.pop('image_file')
        choice_img = deepcopy(image_file)
        url = s3(user,image_file,name)
        choice_type = mr(choice_img)
        type = "1" if choice_type == "Dog" else "2"
        # pet_profile = PetProfile(**validated_data)
        # pet_profile.pet_profile_img = image_file
        # pet_profile.save()
        petprofile = PetProfile.objects.create(
            user=user,
            name=name,
            birthday=birthday,
            type=type,
            gender=gender,
            size=size,
            pet_profile_img=url
        )
        
        return petprofile

    def update(self, instance, validated_data):
        image_file = validated_data.pop('image_file')
        url = s3(instance.user.id, image_file, instance.name)
        instance.pet_profile_img = url
        instance.save()
        return instance

    class Meta:
        model = PetProfile
        fields = '__all__'
        
        extra_kwargs = {
            'type': {
                'required': False,
            }
        }

class UserProfileSerializer(serializers.ModelSerializer):
    
    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            if attr == 'image_file':
                url = s3(instance.user.id, value)
                instance.profile_img = url
            setattr(instance, attr, value)
            instance.save()
        return instance
        
    class Meta:
        model = UserProfile
        fields = '__all__'

class UserSerializer(serializers.ModelSerializer):
    petprofile = PetProfileSerializer(many=True, source="parent", read_only=True)  # 역참조 
    # userprofile = UserProfileSerializer(many=True, source="userprofile_set", read_only=True)  # 역참조 
    articles = ArticleSerializer(many=True, source="article_set", read_only=True)  # 역참조 
    like_articles = serializers.SerializerMethodField()
    phone_num = serializers.SerializerMethodField()
    profile_img = serializers.SerializerMethodField()
    introduction = serializers.SerializerMethodField()

    def get_phone_num(self,obj):
        try:
            return obj.userprofile.phone
        except:
            return f'000-0000-0000'

    def get_profile_img(self,obj):
        try:
            return obj.userprofile.profile_img
        except:
            return f'https://cdn.pixabay.com/photo/2017/09/25/13/12/cocker-spaniel-2785074__480.jpg'
    
    def get_introduction(self,obj):
        try:
            return obj.userprofile.introduction
        except:
            return f'유저님의 마이 페이지입니다'

    def get_like_articles(self, obj):

        article_likes =Article.objects.filter(like=obj.id)
        article_list = []
        for article in article_likes:
            images = Image.objects.filter(article=article)
            comments = Comment.objects.filter(article=article)
            doc = {
                'id': article.id,
                'content': article.content,
                'author':article.user.username,
                'imgurl': [img.imgurl for img  in images],
                'comment': [com.comment for com  in comments]
            }
            article_list.append(doc)     


        return article_list
    
    

    gender_choice = serializers.IntegerField(write_only=True, required=False)
    birthday_date = serializers.DateField(write_only=True, required=False)
    is_active_val = serializers.BooleanField(write_only=True, required=False)

    gender = serializers.SerializerMethodField()
    birthday = serializers.SerializerMethodField()
    show_active = serializers.SerializerMethodField()

    def get_gender(self, obj):
        try:
            return obj.userprofile.gender
        except:
            return f'입력해주세요'
    
    def get_birthday(self, obj):
        try:
            return obj.userprofile.birthday
        except:
            return f'입력해주세요'

    def show_active(self,obj):
        try:
            return obj.userprofile.is_active
        except:
            return f'입력해주세요'



    #     if not data.get("email", "").endswith(EMAIL):
    #         raise serializers.ValidationError(
    #             detail={"error": "네이버, 구글, 카카오 이메일만 가입할 수 있습니다."}
    #         )
    #     if not len(data.get("password", "")) >= 6:
    #         raise serializers.ValidationError(
    #             detail={"error": "password의 길이는 6자리 이상이어야 합니다."}
    #         )

    def create(self, validated_data):

        gender_choice = validated_data.pop("gender_choice")
        birthday_date = validated_data.pop("birthday_date")
        is_active_val = validated_data.pop("is_active_val")
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        UserProfile.objects.create(
            user=user,
            gender=gender_choice,
            birthday=birthday_date,
            is_active=is_active_val,
        )
        return user

    def update(self, instance, validated_data):
        for key, value in validated_data.items():
            if key == "password":
                instance.set_password(value)
                continue
            setattr(instance, key, value)
        instance.save()
        return instance

    class Meta:
        model = User
        # fields = '__all__'
        fields =  ['id', 'password','articles', 'username', 'email', 'gender', 'birthday', 'last_login', 'updated_at', 'created_at', 
        'latitude', 'longitude', 'petprofile', 'birthday_date', 'gender_choice', 'is_active_val', 'like_articles',
        'phone_num', 'profile_img','introduction']

        extra_kwargs = {
            'password': {'write_only': True},
            'email': {
                'error_messages': {'required': '이메일을 입력해주세요', 'invalid': '알맞은 형식의 이메일을 입력해주세요'},
                'required': False
            },
        }

