from django.urls import path
from .views import WalkingMateView, WalkingMateDetailView



urlpatterns = [
    path('', WalkingMateView.as_view()),
    path('<int:pk>/', WalkingMateDetailView.as_view()),
]

