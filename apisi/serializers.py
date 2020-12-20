from rest_framework import serializers
from si.models import Recruit, Sith, RecruitAnswer


class RecruitsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recruit
        fields = ('id', 'name', 'planet', 'age', 'email')


class RecruitQuestionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecruitAnswer
        fields = ('recruit', 'question', 'answer')


class RecruitsDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recruit
        fields = ('id', 'name', 'planet', 'age', 'email', 'sith', 'recruitanswers')


class SithsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sith
        fields = ('id', 'name', 'planet', 'order')


class SithsDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sith
        fields = ('id', 'name', 'planet', 'order', 'recruits')


#   fields = '__all__'





