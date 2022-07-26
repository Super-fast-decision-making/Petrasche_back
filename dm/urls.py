from django.urls import path, include
from . import views


from dm.views import HeaderView, ChatView



urlpatterns = [
    path('', HeaderView.as_view()),
    path('<int:pk>/', ChatView.as_view()),
]


