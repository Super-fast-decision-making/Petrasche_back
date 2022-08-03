from django.contrib import admin
from django.urls import path
from user import views
from rest_framework_simplejwt.views import (
    # TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('', views.UserView.as_view()),
    path('login/', views.TokenObtainPairView.as_view(), name='patrasche_token'),
    path('kakao/', views.KakaoLoginView.as_view(), name='kakao_login'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('authonly/', views.OnlyAuthenticatedUserView.as_view()),
    path('authonly/<int:pk>/', views.OnlyAuthenticatedUserView.as_view()),
    path('userarticle/<int:pk>/', views.PersonalProfilesView.as_view()),
    path('follow/', views.UserFollowingView.as_view()),
    path('mypet/', views.PetView.as_view()),
    path('mypet/<int:pk>/', views.PetDetailView.as_view()),
    path('history/', views.HistoryView.as_view()),
    path('auth/', views.AuthPasswordView.as_view()),
    path('location/<int:pk>/', views.UserLocationView.as_view()),
]
