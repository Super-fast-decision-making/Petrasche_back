from rest_framework import serializers
from .models import User, PetProfile, UserProfile
from article.models import Article, Image, Comment
from article.serializers import ArticleSerializer


EMAIL = ("@naver.com", "@gmail.com", "@kakao.com")

class PetProfileSerializer(serializers.ModelSerializer):

    pet_owner = serializers.SerializerMethodField()

    def get_pet_owner(self, obj):
        return obj.user.username

    class Meta:
        model = PetProfile
        fields = '__all__'


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = '__all__'

class UserSerializer(serializers.ModelSerializer):
    petprofile = PetProfileSerializer(many=True, source="parent", read_only=True)  # 역참조 
    # articles = ArticleSerializer(many=True, source="article_set", read_only=True)  # 역참조 
    like_articles = serializers.SerializerMethodField()

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
        print("***************")
        print('validated_data:', validated_data)
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

    class Meta:
        model = User
        # fields = '__all__'
        fields =  ['id', 'password', 'username', 'email', 'gender', 'birthday', 'last_login', 'updated_at', 'created_at', 'latitude', 'longitude', 'petprofile', 'birthday_date', 'gender_choice', 'is_active_val', 'like_articles']

        extra_kwargs = {
            'password': {'write_only': True},
            'email': {
                'error_messages': {'required': '이메일을 입력해주세요', 'invalid': '알맞은 형식의 이메일을 입력해주세요'},
                'required': False
            },
        }

