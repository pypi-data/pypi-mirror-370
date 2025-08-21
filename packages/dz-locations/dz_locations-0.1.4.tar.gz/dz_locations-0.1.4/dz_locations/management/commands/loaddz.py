import json
from django.core.management.base import BaseCommand
from dz_locations.models import Wilaya, Commune
from pathlib import Path

class Command(BaseCommand):
    help = "Load Algerian states and communes from JSON"

    def handle(self, *args, **kwargs):
        # file_path = Path(__file__).resolve().parent.parent.parent / "dz_data.json"
        # with open(file_path, 'r', encoding='utf-8') as file:
        #     data = json.load(file)
        #     for wilaya_data in data:
        #         wilaya, created = Wilaya.objects.get_or_create(
        #             name_ar=wilaya_data['name_ar'],
        #             defaults={'name_fr': wilaya_data['name_fr']}
        #         )
        #         for commune_data in wilaya_data['communes']:
        #             Commune.objects.get_or_create(
        #                 wilaya=wilaya,
        #                 name_ar=commune_data['name_ar'],
        #                 defaults={'name_fr': commune_data['name_fr']}
        #             )
        self.stdout.write(self.style.SUCCESS("DZ Locations loaded successfully!"))
