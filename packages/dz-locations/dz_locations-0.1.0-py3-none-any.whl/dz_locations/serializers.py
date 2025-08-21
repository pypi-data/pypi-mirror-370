from rest_framework import serializers
from .models import Wilaya, Commune

class CommuneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Commune
        fields = ['id', 'name_ar', 'name_fr']

class WilayaSerializer(serializers.ModelSerializer):
    communes = CommuneSerializer(many=True, read_only=True)

    class Meta:
        model = Wilaya
        fields = ['id', 'name_ar', 'name_fr', 'communes']
