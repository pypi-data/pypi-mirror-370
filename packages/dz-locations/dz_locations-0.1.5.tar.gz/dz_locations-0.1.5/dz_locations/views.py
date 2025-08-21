from rest_framework import generics
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Wilaya
from .serializers import WilayaSerializer

class WilayaListAPI(generics.ListAPIView):
    queryset = Wilaya.objects.all()
    serializer_class = WilayaSerializer



def get_wliaya(request , code): 
    try:
        wilaya = get_object_or_404(Wilaya, code=code)
        serializer = WilayaSerializer(wilaya)
        return Response(serializer.data , status=200)
    except Wilaya.DoesNotExist:
        return Response({"error": "Wilaya not found"}, status=404)