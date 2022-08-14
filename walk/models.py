from django.db import models
from ckeditor_uploader.fields import RichTextUploadingField
from django.urls import register_converter
from user.models import BaseModel, User
import datetime
# Create your models here.

class WalkingMate(BaseModel):#relation_name
    host=models.ForeignKey('user.User', related_name='event', verbose_name="호스트", on_delete=models.CASCADE)
    image = models.URLField(max_length=200, null=True, blank=True)
    start_date= models.DateField('날짜', null=True)
    start_time=models.DateTimeField('시작 시간')
    end_time=models.DateTimeField('종료 시간')
    region=models.CharField('지역', max_length=30)
    place=models.CharField('만남 장소', max_length=200)
    gender=models.CharField('참여자 성별', max_length=10)
    size=models.CharField('사이즈', max_length=30)
    people_num=models.CharField('참여자수', max_length=20)
    contents= RichTextUploadingField('내용', blank=True, null=True)
    attending_user = models.ManyToManyField('user.User', related_name='program', verbose_name="참여자 명단", blank=True)
    
    @property
    def deadeline_status(self):
        ''' 시간이 지나거나 사람 인원이 다 차면 False=마감, True=마감전 '''
        if (self.start_time<=datetime.datetime.now()):       
            return False
        return True

    def __str__(self):
        return f'{self.host.username}의 모임'