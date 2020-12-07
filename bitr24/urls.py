from django.urls import path
from .views import *
from django.views.decorators.csrf import csrf_exempt


urlpatterns = [
    path('tg/',  csrf_exempt(Tg.as_view()), name='tg_url'),
    path('chat/', chats_list, name='chats_list_url'),
    path('chat/create/', ChatCreate.as_view(), name='chat_create_url'),
    path('chat/<str:slug>/', ChatDetail.as_view(), name='chat_detail_url'),
    path('chat/<str:slug>/update/', ChatUpdate.as_view(), name='chat_update_url'),
    path('chat/<str:slug>/delete/', ChatDelete.as_view(), name='chat_delete_url'),
    path('bitr/', bitrs_list, name='bitrs_list_url'),
    path('bitr/create/', BitrCreate.as_view(), name='bitr_create_url'),
    path('bitr/<str:slug>/', BitrDetail.as_view(), name='bitr_detail_url'),
    path('bitr/<str:slug>/update/', BitrUpdate.as_view(), name='bitr_update_url'),
    path('bitr/<str:slug>/delete/', BitrDelete.as_view(), name='bitr_delete_url'),
]

