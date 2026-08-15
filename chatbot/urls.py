from django.urls import path
from .views import ChatView, chat_ui

urlpatterns = [
    path("chat/", ChatView.as_view(), name="chat"),
]

