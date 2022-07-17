from django.db import models
from user.models import User
# Create your models here.
from datetime import datetime



# class Channel(models.Model):
#     owner = models.ForeignKey(User, on_delete=models.CASCADE)
#     name = models.CharField(unique=True, max_length=120)
#     image_url = models.URLField(null=True, blank=True)

#     def __str__(self):
#         return self.name


class Message(models.Model):
    from_user = models.ForeignKey(User, on_delete=models.CASCADE)
    to_user = models.ForeignKey(User, )
    # channel = models.ForeignKey(Channel, on_delete=models.CASCADE)
    message = models.CharField(max_length=200)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username} said {self.message}'

    class Meta:
        ordering = ['timestamp']