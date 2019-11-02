from django.urls import path
from .views import index

app_name = 'bot'

urlpatterns = [
    path('', index),
]

