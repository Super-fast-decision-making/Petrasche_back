from time import time
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from tournament import serializers
from tournament.models import TournamentAttendant, PetEventPeriod, ParticipatioTime
from tournament.serializers import TournamentAttendantSerializer, PetEventPeriodSerializer
from datetime import datetime, timedelta

class TournamentAttendantView(APIView):
    def get(self, request):
        attendants = TournamentAttendant.objects.all()
        serializer = TournamentAttendantSerializer(attendants, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request):
        request.data['user_id'] = request.user.id
        pet_event = PetEventPeriod.objects.get(id=request.data['event'])
        if pet_event.tournament_item.filter(user_id=request.user.id).exists():
            return Response({"message":"이벤트에 이미 참여 되었습니다."}, status=status.HTTP_400_BAD_REQUEST)
        serializer = TournamentAttendantSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        pet = TournamentAttendant.objects.get(pk=pk)
        for i in pet.peteventperiod_set.all():
            period = PetEventPeriod.objects.get(id=i.id)
        user = period.participants.filter(user_id=request.user.id)
        if user.exists():
            # 1시간에 1번 이벤트 참여 로직
            # if user.last().participation > (datetime.now() + timedelta(hours=1)):
            #     return Response({"message":"1시간에 1번씩 참여가 가능합니다."}, status=status.HTTP_400_BAD_REQUEST)
            return Response({"message":"이미 참여하셨습니다."}, status=status.HTTP_400_BAD_REQUEST)
        participiatiotime = ParticipatioTime.objects.create(user_id=request.user, participation=datetime.now())
        period.participants.add(participiatiotime)
        period.save()
        pet.point += 1
        pet.save()
        serializers = TournamentAttendantSerializer(pet)
        return Response(serializers.data, status=status.HTTP_200_OK)

class PetEventPeriodView(APIView):
    def get(self, request):
        periods = PetEventPeriod.objects.all().order_by('-start_time')
        serializer = PetEventPeriodSerializer(periods, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request):
        serializer = PetEventPeriodSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PetEventPeriodDetailView(APIView):
    def get(self, request, pk):
        period = PetEventPeriod.objects.get(pk=pk)
        if period.end_time < datetime.now():
            return Response({"message" : "종료된 이벤트 입니다."}, status=status.HTTP_400_BAD_REQUEST)
        elif period.start_time > datetime.now():
            return Response({"message" : "시작되지 않은 이벤트 입니다."}, status=status.HTTP_400_BAD_REQUEST)
        serializer = PetEventPeriodSerializer(period)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, pk):
        try:
            period = PetEventPeriod.objects.get(pk=pk)
        except:
            return Response({"message" : "존재하지 않는 이벤트 입니다."}, status=status.HTTP_400_BAD_REQUEST)
        period.delete()
        return Response({"message" : "삭제 완료"}, status=status.HTTP_200_OK)