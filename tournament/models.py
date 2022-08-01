from django.db import models
from user.models import User, BaseModel

class TournamentAttendant(BaseModel):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    image = models.URLField("이벤트이미지", default="")
    point = models.IntegerField("포인트", default=0)

    def __str__(self):
        return self.user_id.username

class ParticipatioTime(BaseModel):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    participation = models.DateTimeField("투표참여시간")

    def __str__(self):
        return f'{self.user_id.username} - {self.participation}'        

class PetEventPeriod(BaseModel):
    tournament_item = models.ManyToManyField(TournamentAttendant, verbose_name="토너먼트", blank=True)
    participants = models.ManyToManyField(ParticipatioTime, verbose_name="투표참여자", blank=True)
    event_name = models.CharField("이벤트", max_length=100)
    event_desc = models.CharField("이벤트설명", max_length=500)
    start_time = models.DateTimeField("시작시간")
    end_time = models.DateTimeField("종료시간")

    def __str__(self):
        return self.event_name


