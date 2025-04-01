from .models import *
from rest_framework import serializers

class UserRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model =UserRegister
        fields='__all__'

class RestarauntSerializer(serializers.ModelSerializer):
    class Meta:
        model=Restaraunt
        fields="__all__"