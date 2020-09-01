from django.contrib import admin
from django.urls import path
from .views import RecruitsListView
# CarCreateView, CarsListView, CarDetailView

app_name = 'si'
urlpatterns = [
    path('recruits/', RecruitsListView.as_view()),
    # path('car/create', CarCreateView.as_view()),
    # path('car/detail/<int:pk>', CarDetailView.as_view()),
]
