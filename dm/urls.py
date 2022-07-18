from django.urls import path, include
from . import views


from dm.views import HeaderView



urlpatterns = [
    path('', HeaderView.as_view()),
]


