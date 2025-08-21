from django.urls import path
from .views import get_wilaya_list , get_wilaya

urlpatterns = [
    path('wilayas/', get_wilaya_list, name='get-wilaya-list'),
    path('wilayas/<str:code>/', get_wilaya, name='get-wilaya-by-code'),
]
