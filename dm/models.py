from turtle import Turtle
from django.db import models
from django.dispatch import receiver
# Create your models here.

class Message(models.Model):
    sender = models.ForeignKey('user.User', related_name="sent_messanges", on_delete=models.CASCADE)
    receiver = models.ForeignKey('user.User', related_name="received_messages", on_delete=models.CASCADE)
    message = models.TextField()
    seen = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ("date_created",)