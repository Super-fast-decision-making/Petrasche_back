from email import header
from django.db import models
from user.models import BaseModel, User
from django.db.models import Q

# 커스텀 매니저
class HeaderManager(models.Manager):
    def by_user(self, **kwargs):
        user = kwargs.get('user')
        lookup = Q(sender=user)|Q(receiver=user)
        result = self.get_queryset().filter(lookup).distinct() # lookup결과에 대한 중복 발생시 distinct함수로 중복 제거
        return result


class Header(BaseModel):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='sender')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='receiver')
    objects = HeaderManager()
    
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["sender", "receiver"], name="sender, receiver는 한개의 헤더만 가질수 있다.")
            ]
    
    def __str__(self):
        return f"{self.id}///{self.sender}, {self.receiver}"

class Message(BaseModel):
    header = models.ForeignKey(Header, on_delete=models.CASCADE, null=True, blank=True, related_name='header')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    message = models.CharField(max_length=500)
    
    class Meta:
        ordering = ['created_at']
        
    def __str__(self):
        return f"{self.header} /// {self.sender} : '{self.message}'"
    
    

