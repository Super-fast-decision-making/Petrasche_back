
from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path('chat/<int:room_id>', consumers.ChatConsumer.as_asgi()),
    # path('chat/user/<int:user_id>', consumers.ChatAlarm.as_asgi()),
]