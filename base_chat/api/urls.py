from django.urls import path

from .views import ChatViews, MessageHistory, UserAPIRegister

urlpatterns = [
    path('list/', ChatViews.as_view()),
    path('chat/<int:chat_id>/', MessageHistory.as_view()),
    path('user/', UserAPIRegister.as_view())
]
