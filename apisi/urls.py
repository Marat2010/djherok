from django.urls import path
from .views import RecruitsListView, RecruitsDetailView, SithsListView, SithsDetailView

app_name = 'si'
urlpatterns = [
    path('recruits/', RecruitsListView.as_view()),
    path('recruits/<int:pk>', RecruitsDetailView.as_view()),
    path('siths/', SithsListView.as_view()),
    path('siths/<int:pk>', SithsDetailView.as_view()),
]

