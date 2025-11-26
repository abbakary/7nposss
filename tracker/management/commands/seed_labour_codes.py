"""
Management command to seed the Labour Codes table.
Run with: python manage.py seed_labour_codes
"""

from django.core.management.base import BaseCommand
from tracker.models import LabourCode


LABOUR_CODES_DATA = [
    {"code": "22007", "description": "OIL SERVICE (FILTER) FOR 4X4", "category": "labour"},
    {"code": "21044", "description": "WHEEL BALANCE ALLOY RIMS", "category": "tyre service"},
    {"code": "21031", "description": "REPAIR & A/C PASSENGER", "category": "labour"},
    {"code": "32004", "description": "WHEEL BALANCE TRUCK", "category": "tyre service"},
    {"code": "21003", "description": "WHEEL BALANCE TRUCK", "category": "tyre service"},
    {"code": "41005", "description": "TRAILER ALIGNMENT, MECHANICAL SUSPENSION, PER AXLE", "category": "tyre service / makill"},
    {"code": "41003", "description": "STEERING AXLE ALIGNMENT, NON-MICHELIN TYPE", "category": "tyre service / makill"},
    {"code": "21037", "description": "TYRE FITTING-TRUCK", "category": "tyre service"},
    {"code": "21035", "description": "WHEEL BALANCE 15-16\"", "category": "tyre service"},
    {"code": "21002", "description": "WHEEL BALANCE 15-16\"", "category": "tyre service"},
    {"code": "23030", "description": "TYRE FITTING SMALL", "category": "tyre service"},
    {"code": "21013", "description": "TYRE ROTATION SERVICE 4X4", "category": "tyre service"},
    {"code": "21020", "description": "WHEEL ALIGNMENT BIG", "category": "tyre service"},
    {"code": "21017", "description": "TYRE ROTATION TRUCK", "category": "tyre service"},
    {"code": "21027", "description": "TYRE ROTATION SERVICE - TRUCK", "category": "tyre service"},
    {"code": "22024", "description": "VEHICLE DIAGNOSIS FOR 4X4CAR", "category": "labour"},
    {"code": "22815", "description": "VEHICLE DIAGNOSIS FOR 4X4", "category": "labour"},
    {"code": "22816", "description": "VEHICLE DIAGNOSIS FOR TRUCK", "category": "labour"},
    {"code": "21036", "description": "GREASE SERVICE 4x4", "category": "labour"},
    {"code": "22005", "description": "OIL SERVICE (OIL FILTER, AIR FILTER, SOLI) FOR PASSENGER CAR", "category": "labour"},
    {"code": "22006", "description": "OIL SERVICE (OIL FILTER, AIR FILTER, ADDITIONAL DIFF OIL, FUEL FILTER, HYDRAULIC, ENGINE COOLANT, BRAKE FLUID SOLI) FOR PASSENGER", "category": "labour"},
    {"code": "22202", "description": "SHOCK ABSORBERS SERVICE FOR TRUCK", "category": "labour"},
    {"code": "22009", "description": "SHOCK ABSORBERS SERVICE FOR TRUCK", "category": "labour"},
    {"code": "22011", "description": "AC SERVICE FOR PASSENGER CAR", "category": "labour"},
    {"code": "22012", "description": "AC SERVICE FOR 4X4", "category": "labour"},
    {"code": "22013", "description": "AC SERVICE FOR TRUCK", "category": "labour"},
    {"code": "31004", "description": "TYRE MAINTENANCE SERVICE", "category": "tyre service"},
    {"code": "31005", "description": "SPARE SERVICE", "category": "labour"},
    {"code": "33001", "description": "INSPECTION", "category": "labour"},
    {"code": "32007", "description": "SERVICE FOR STAFF CARS", "category": "labour"},
    {"code": "38001", "description": "TBL SERVICE CONTRACT KWANZA", "category": "labour"},
    {"code": "11011", "description": "WORKMANSHIP", "category": "labour"},
    {"code": "38002", "description": "TYRE MANAGEMENT SERVICE CHARGE (BUDIN)", "category": "labour"},
    {"code": "12005", "description": "DELIVERY CHARGES", "category": "labour"},
    {"code": "22001", "description": "BRAKE PAD FITMENT PER AXLE FOR PASSENGER CAR", "category": "labour"},
    {"code": "22004", "description": "BRAKE PAD FITMENT PER AXLE FOR TRUCK", "category": "labour"},
    {"code": "22014", "description": "VEHICLE DIAGNOSIS FOR PASSENGER CAR", "category": "labour"},
    {"code": "22015", "description": "VEHICLE DIAGNOSIS FOR 4X4", "category": "labour"},
    {"code": "22016", "description": "VEHICLE DIAGNOSIS FOR TRUCK", "category": "labour"},
    {"code": "11012", "description": "SERVICE CONTRACTS", "category": "labour"},
    {"code": "11013", "description": "TYRE SERVICE CONTRACTS", "category": "tyre service"},
    {"code": "21096", "description": "GREACE SERVICE 4x4", "category": "labour"},
    {"code": "22008", "description": "SHOCK ABSORBERS SERVICE FOR TRUCK", "category": "labour"},
    {"code": "33002", "description": "INTEGRATED SERVICE", "category": "labour"},
]


class Command(BaseCommand):
    help = "Seed the Labour Codes table with data from the provided spreadsheet"

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear all existing labour codes before seeding'
        )

    def handle(self, *args, **options):
        if options['clear']:
            count = LabourCode.objects.count()
            LabourCode.objects.all().delete()
            self.stdout.write(self.style.SUCCESS(f'✓ Cleared {count} existing labour codes'))
        
        self.stdout.write(self.style.SUCCESS('=' * 80))
        self.stdout.write(self.style.SUCCESS('SEEDING LABOUR CODES TABLE'))
        self.stdout.write(self.style.SUCCESS('=' * 80))
        
        created_count = 0
        updated_count = 0
        
        for data in LABOUR_CODES_DATA:
            code = data['code'].strip()
            description = data['description'].strip()
            category = data['category'].strip().lower()
            
            obj, created = LabourCode.objects.update_or_create(
                code=code,
                defaults={
                    'description': description,
                    'category': category,
                    'is_active': True
                }
            )
            
            if created:
                created_count += 1
                status = "✓ Created"
            else:
                updated_count += 1
                status = "• Updated"
            
            self.stdout.write(f"{status}: {code} - {description[:50]}... ({category})")
        
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('=' * 80))
        self.stdout.write(self.style.SUCCESS('SEEDING COMPLETE'))
        self.stdout.write(self.style.SUCCESS(f'  Created: {created_count}'))
        self.stdout.write(self.style.SUCCESS(f'  Updated: {updated_count}'))
        self.stdout.write(self.style.SUCCESS(f'  Total:   {LabourCode.objects.count()}'))
        self.stdout.write(self.style.SUCCESS('=' * 80))
