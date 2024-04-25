from django.urls import path
from . import views

urlpatterns = [
    path("list-chats/", views.UserChatsView.as_view(), name="list-chats"),
    path(
        "chat-with-ai/<str:chat_id>", views.UserChatsView.as_view(), name="start-a-chat"
    ),
    path("create-new-chat/", views.createNewChat, name="Create-new-chat"),
    path("delete/<str:chat_id>", views.UserChatsView.as_view(), name="delete-a-chat"),
    path("list-message/<str:chat_id>", views.getAllMessages, name="get-all-messages"),
    path("recent-chats/", views.RecentChatsView.as_view(), name="recent-chat"),
    path("recent-messages/", views.getMessages, name="get-recent-messages"),
    path("get-chat-name/", views.getChatName, name="get-chat-name"),
]
