from django.urls import path
from .views import *
# , TbxView, TbxListViev, TbxDetailView
# from .views import chats_list, chat_detail, bitrs_list, bitr_detail

urlpatterns = [
    # path('', index),
    path('auth/', auth, name='auth'),
    path('', chats_list, name='chats_list_url'),
    path('chat/<str:slug>/', ChatDetail.as_view(), name='chat_detail_url'),
    path('bitrs/', bitrs_list, name='bitrs_list_url'),
    path('bitr/<str:slug>/', BitrDetail.as_view(), name='bitr_detail_url')
]

# path('tbx/', TbxView.as_view(), name='tbx'),
# path('tbx_all/', TbxListViev.as_view(), name='tbx_all'),
# path('tbx_all/<slug:tbx_slug>', TbxDetailView.as_view(), name='tbx_detail'),
# path('add/', RecruitsCreateView.as_view(), name='add'),
# path('<int:planet_id>/', by_planet, name='by_planet'),
