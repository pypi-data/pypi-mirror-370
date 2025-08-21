from django.http import JsonResponse
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.shortcuts import get_object_or_404
from .models import Wilaya , Commune
from .serializers import WilayaSerializer



@api_view(['GET'])
def get_wilaya_list(request):
    wilayas = Wilaya.objects.all()
    serializer = WilayaSerializer(wilayas, many=True)
    return Response(serializer.data, status=200)


@api_view(['GET'])
def get_wilaya(request , code): 
    try:
        wilaya = get_object_or_404(Wilaya, code=code)
        serializer = WilayaSerializer(wilaya)
        return Response(serializer.data , status=200)
    except Wilaya.DoesNotExist:
        return Response({"error": "Wilaya not found"}, status=404)
    