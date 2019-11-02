from django.urls import path
from .views import UpdateBot
# from .views import index

app_name = 'bot'

urlpatterns = [
    path('telegram', UpdateBot.as_view(), name='update'),
    # path('', index),
]

