from django.urls import path
from .views import WilayaListAPI

urlpatterns = [
    path('api/wilayas/', WilayaListAPI.as_view(), name='wilaya-list'),
]
