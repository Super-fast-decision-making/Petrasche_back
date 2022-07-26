from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from tournament import serializers
from tournament.models import TournamentAttendant, PetEventPeriod
from tournament.serializers import TournamentAttendantSerializer, PetEventPeriodSerializer

class TournamentAttendantView(APIView):
    def get(self, request):
        attendants = TournamentAttendant.objects.all()
        serializer = TournamentAttendantSerializer(attendants, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request):
        request.data['user_id'] = request.user.id
        serializer = TournamentAttendantSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        pet = TournamentAttendant.objects.get(pk=pk)
        pet.point += 1
        pet.save()
        serializers = TournamentAttendantSerializer(pet)
        return Response(serializers.data, status=status.HTTP_200_OK)

class PetEventPeriodView(APIView):
    def get(self, request):
        periods = PetEventPeriod.objects.all()
        serializer = PetEventPeriodSerializer(periods, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request):
        serializer = PetEventPeriodSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)