from django.urls import path
from tournament import views


urlpatterns = [
    path('', views.TournamentAttendantView.as_view()),
    path('period/', views.PetEventPeriodView.as_view()),
    path('period/<int:pk>/', views.PetEventPeriodDetailView.as_view()),
    path('<int:pk>/', views.TournamentAttendantView.as_view()),
]