from django.shortcuts import render
from rest_framework import generics
from .serializers import RecruitsSerializer, RecruitsDetailSerializer, SithsSerializer, SithsDetailSerializer
from si.models import Recruit, Sith


class RecruitsListView(generics.ListAPIView):
    serializer_class = RecruitsSerializer
    queryset = Recruit.objects.all()


class RecruitsDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = RecruitsDetailSerializer
    queryset = Recruit.objects.all()


class SithsListView(generics.ListAPIView):
    serializer_class = SithsSerializer
    queryset = Sith.objects.all()


class SithsDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = SithsDetailSerializer
    queryset = Sith.objects.all()


