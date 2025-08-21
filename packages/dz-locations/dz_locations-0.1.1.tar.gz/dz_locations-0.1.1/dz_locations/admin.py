from django.contrib import admin
from .models import Wilaya, Commune

@admin.register(Wilaya)
class WilayaAdmin(admin.ModelAdmin):
    search_fields = ['name_ar', 'name_fr']
    list_display = ['name_ar', 'name_fr']

@admin.register(Commune)
class CommuneAdmin(admin.ModelAdmin):
    search_fields = ['name_ar', 'name_fr', 'wilaya__name_ar']
    list_display = ['name_ar', 'name_fr', 'wilaya']
    autocomplete_fields = ['wilaya']
