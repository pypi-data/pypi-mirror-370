from rest_framework import generics
from .models import Wilaya
from .serializers import WilayaSerializer

class WilayaListAPI(generics.ListAPIView):
    queryset = Wilaya.objects.all()
    serializer_class = WilayaSerializer
