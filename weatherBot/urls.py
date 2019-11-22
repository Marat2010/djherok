from django.urls import path
from .views import index

urlpatterns = [
    # path('', index, name='ajax_get_coords'),
    path('', index),
]

