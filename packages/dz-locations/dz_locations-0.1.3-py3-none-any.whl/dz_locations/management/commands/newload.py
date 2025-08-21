import json
from django.core.management.base import BaseCommand
from dz_locations.models import Wilaya, Commune
from pathlib import Path





file_wilaya = Path(__file__).resolve().parent.parent.parent / "wilayas.json"
file_commune = Path(__file__).resolve().parent.parent.parent / "communes.json"
         


def get_communes_by_wilaya(wilaya_code):
   with open(file_commune, 'r', encoding='utf-8') as file:
      communes_data = json.load(file)
   return [commune for commune in communes_data if commune['wilaya_id'] == wilaya_code]

class Command(BaseCommand):
      help = "Load Algerian states and communes from JSON"
      def handle(self, *args, **kwargs):

         with open(file_wilaya, 'r', encoding='utf-8') as file:
            wilayas_data = json.load(file)
         
         for wilaya_data in wilayas_data:
            wilaya, created = Wilaya.objects.get_or_create(
               code=wilaya_data['code'],
               defaults={
                  'name': wilaya_data['name'],
                  'ar_name': wilaya_data['ar_name'],
                  'longitude': float(wilaya_data['longitude']),
                  'latitude': float(wilaya_data['latitude'])
               }
            )
            if created:
               self.stdout.write(self.style.SUCCESS(f"Created Wilaya: {wilaya.name}"))
            else:
               self.stdout.write(self.style.WARNING(f"Wilaya already exists: {wilaya.name}"))
            
            
            communes = get_communes_by_wilaya(wilaya.code)
            for commune_data in communes:
               commune, created = Commune.objects.get_or_create(
                  post_code=commune_data['post_code'],
                  wilaya=wilaya,
                  defaults={
                     'name': commune_data['name'],
                     'ar_name': commune_data['ar_name'],
                     'longitude': float(commune_data['longitude']),
                     'latitude': float(commune_data['latitude']),
                  }
               )


         self.stdout.write(self.style.SUCCESS("All Wilayas and Communes have been loaded successfully !"))
    
      
            