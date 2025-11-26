from django.core.management.base import BaseCommand
from tracker.models import DelayReasonCategory, DelayReason


class Command(BaseCommand):
    help = 'Seed delay reason categories and specific reasons for orders exceeding 9 hours'

    def handle(self, *args, **options):
        delay_reasons_data = {
            'parts': {
                'display': 'Parts-Related Delays',
                'reasons': [
                    'Spare parts out of stock',
                    'Incorrect part delivered or mismatch with vehicle model',
                    'Delayed parts shipment from supplier',
                    'Need for special-order parts (rare or imported)',
                ]
            },
            'technical': {
                'display': 'Technical / Diagnostic Issues',
                'reasons': [
                    'Unexpected faults discovered during routine service',
                    'Complex diagnostics needed (electrical issues, sensor faults, ECU problems)',
                    'Need for specialist technician to inspect certain problems',
                    'Software updates or reprogramming taking longer',
                ]
            },
            'workload': {
                'display': 'High Workload / Operational Capacity',
                'reasons': [
                    'High number of vehicles in queue',
                    'Insufficient technicians available (leave, training, or peak hours)',
                    'Workshop overload due to special promotions or seasonal rush',
                    'Equipment or service bay not available',
                ]
            },
            'customer': {
                'display': 'Customer-Related Causes',
                'reasons': [
                    'Customer delayed approval for additional repairs or parts',
                    'Inaccurate information provided about the issue',
                    'Late vehicle drop-off vs. scheduled time',
                ]
            },
            'administrative': {
                'display': 'Administrative / System Issues',
                'reasons': [
                    'POS system or billing delays',
                    'Job order not updated correctly',
                    'Miscommunication between front desk and workshop',
                    'Warranty validation delays',
                ]
            },
            'quality': {
                'display': 'Quality-Control & Testing Delays',
                'reasons': [
                    'Extended road testing required',
                    'Rechecking after repair for safety or accuracy',
                    'Final inspection backlog',
                ]
            },
            'external': {
                'display': 'External / Environmental Factors',
                'reasons': [
                    'Power outage',
                    'Bad weather affecting testing (e.g., rain for brake tests)',
                    'Transport limitations (for outsourced tasks like painting)',
                ]
            },
        }

        created_count = 0
        reason_count = 0

        for category_key, category_data in delay_reasons_data.items():
            # Create or get category
            category, created = DelayReasonCategory.objects.get_or_create(
                category=category_key,
                defaults={'description': category_data['display']}
            )

            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created category: {category_data["display"]}')
                )

            # Create reasons for this category
            for reason_text in category_data['reasons']:
                reason, created = DelayReason.objects.get_or_create(
                    category=category,
                    reason_text=reason_text,
                )
                if created:
                    reason_count += 1
                    self.stdout.write(f'  - Created reason: {reason_text}')

        self.stdout.write(
            self.style.SUCCESS(
                f'\n✓ Successfully seeded delay reasons!\n'
                f'  Categories created: {created_count}\n'
                f'  Reasons created: {reason_count}'
            )
        )
