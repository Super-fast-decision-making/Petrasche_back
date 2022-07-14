from django.urls import path
from . import views
from .views import (
    MessageCreateView,
    MessageListView,
    ChannelCreateAPIView,
    ChannelListAPIView
)


urlpatterns = [
    path('', ChannelListAPIView.as_view(), name='channel-list'),
    path('create/', ChannelCreateAPIView.as_view(), name='channel-create'),
    path('<int:channel_id>/', MessageListView.as_view(), name='message-list'),
    path('<int:channel_id>/send/',
         MessageCreateView.as_view(), name='message-create'),
]