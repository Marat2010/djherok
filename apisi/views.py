from django.shortcuts import render
from rest_framework import generics
from .serializers import RecruitsListSerializer
from si.models import Recruit


class RecruitsListView(generics.ListAPIView):
    serializer_class = RecruitsListSerializer
    queryset = Recruit.objects.all()
