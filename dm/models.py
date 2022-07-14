from django.db import models
from user.models import User
# Create your models here.



class Channel(models.Model):
    name = models.CharField(unique=True, max_length=120)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    image_url = models.URLField(null=True, blank=True)

    def __str__(self):
        return self.name


class Message(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE)
    message = models.CharField(max_length=200)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username} said {self.message}'

    class Meta:
        ordering = ['timestamp']