from django.contrib import admin
from tournament.models import TournamentAttendant, PetEventPeriod, ParticipatioTime

admin.site.register(TournamentAttendant)
admin.site.register(PetEventPeriod)
admin.site.register(ParticipatioTime)