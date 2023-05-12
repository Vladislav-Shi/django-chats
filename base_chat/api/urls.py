from django.urls import path

from .views import ChatViews, MessageHistory, UserAPIRegister, UserAPI, SingleChatViews

urlpatterns = [
    path('list/', ChatViews.as_view()),
    path('chat/<int:chat_id>/', SingleChatViews.as_view()),
    path('chat/<int:chat_id>/messages/', MessageHistory.as_view()),
    path('user/register/', UserAPIRegister.as_view()),
    path('user/list/', UserAPI.as_view()),
]
