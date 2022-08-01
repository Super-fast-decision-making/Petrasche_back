from django.urls import path, include
from . import views


from dm.views import HeaderView, ChatView, UserHeaderView


## #####
urlpatterns = [
    path('', HeaderView.as_view()),
    path('<int:pk>/', ChatView.as_view()),
    path('userheader/<int:pk>/', UserHeaderView.as_view()),
]


