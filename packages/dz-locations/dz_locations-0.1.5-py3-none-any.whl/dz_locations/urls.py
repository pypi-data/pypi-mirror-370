from django.urls import path
from .views import WilayaListAPI , get_wliaya

urlpatterns = [
    path('wilayas/', WilayaListAPI.as_view(), name='wilaya-list'),
    path('wilaya/<str:code>/', get_wliaya, name='get-wilaya-by-code'),
]
