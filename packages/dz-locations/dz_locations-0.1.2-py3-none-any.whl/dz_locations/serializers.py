from rest_framework import serializers
from .models import Wilaya, Commune

class CommuneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Commune
        fields = [
            "id",
            "post_code",
            "name",
            "ar_name",
            "longitude",
            "latitude",
            "wilaya"
        ]
        read_only_fields = ["id"]

class WilayaSerializer(serializers.ModelSerializer):
    communes = CommuneSerializer(many=True, read_only=True)

    class Meta:
        model = Wilaya
        fields = [
            "id",
            "code",
            "name",
            "ar_name",
            "longitude",
            "latitude",
            "communes"
        ]
        read_only_fields = ["id"]
