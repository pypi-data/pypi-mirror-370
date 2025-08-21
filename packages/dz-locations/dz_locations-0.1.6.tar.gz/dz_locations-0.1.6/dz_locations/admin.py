from django.contrib import admin
from .models import Wilaya, Commune

@admin.register(Wilaya)
class WilayaAdmin(admin.ModelAdmin):
    search_fields = ['name', 'code']
    list_display = ['name', 'code' , 'ar_name']
    ordering = ['code']
    

@admin.register(Commune)
class CommuneAdmin(admin.ModelAdmin):
    search_fields = ['name', 'post_code']
    list_display = ['name', 'ar_name' ,'post_code', 'wilaya']
    autocomplete_fields = ['wilaya']
    ordering = ['post_code']
