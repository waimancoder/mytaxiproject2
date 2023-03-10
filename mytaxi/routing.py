from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    # add more WebSocket routes here
    re_path(r'ws/dummy/$', consumers.DummyConsumer.as_asgi()),
]

