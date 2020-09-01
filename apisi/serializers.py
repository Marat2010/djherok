from rest_framework import serializers
from si.models import Recruit


class RecruitsListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recruit
        fields = ('id', 'name', 'planet', 'age', 'email')


# class CarDetailSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Car
#         fields = '__all__'
#         # fields = ('vin', 'color', 'brand', 'car_type', 'user')





