from rest_framework import serializers
from si.models import Recruit, Sith


class RecruitsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recruit
        fields = ('id', 'name', 'planet', 'age', 'email')


class RecruitsDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recruit
        fields = ('id', 'name', 'planet', 'age', 'email')


class SithsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sith
        fields = ('id', 'name', 'planet', 'order')


class SithsDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sith
        fields = ('id', 'name', 'planet', 'order')


#   fields = '__all__'





