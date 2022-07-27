from django.urls import path
from .views import WalkingMateView, WalkingMateDetailView, WalkingMateAttenderView



urlpatterns = [
    path('', WalkingMateView.as_view()),
    path('attend/<int:pk>/', WalkingMateAttenderView.as_view()),
    path('<int:pk>/', WalkingMateDetailView.as_view()),
]

