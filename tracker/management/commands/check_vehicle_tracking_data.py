from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
import logging
from tracker.models import Vehicle, Invoice, Customer, Order, Branch, InvoiceLineItem

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Check and diagnose vehicle tracking data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--seed',
            action='store_true',
            help='Create sample invoices with vehicles if data is missing'
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('\n=== VEHICLE TRACKING DATA DIAGNOSTIC ===\n'))

        # Check counts
        customer_count = Customer.objects.count()
        vehicle_count = Vehicle.objects.count()
        invoice_count = Invoice.objects.count()
        order_count = Order.objects.count()
        branch_count = Branch.objects.count()

        self.stdout.write(f"Total Branches: {branch_count}")
        self.stdout.write(f"Total Customers: {customer_count}")
        self.stdout.write(f"Total Vehicles: {vehicle_count}")
        self.stdout.write(f"Total Invoices: {invoice_count}")
        self.stdout.write(f"Total Orders: {order_count}")

        # Check for recent invoices (30 days)
        today = timezone.now().date()
        thirty_days_ago = today - timedelta(days=30)

        recent_invoices = Invoice.objects.filter(
            invoice_date__range=[thirty_days_ago, today]
        ).count()

        recent_vehicles = Vehicle.objects.filter(
            invoices__invoice_date__range=[thirty_days_ago, today]
        ).distinct().count()

        self.stdout.write(f"\nInvoices in last 30 days: {recent_invoices}")
        self.stdout.write(f"Vehicles with invoices in last 30 days: {recent_vehicles}")

        # Check if we should seed data
        if recent_invoices == 0 and options['seed']:
            self.stdout.write(self.style.WARNING('\nNo recent invoices found. Creating sample data...'))
            self.seed_sample_data()
            self.stdout.write(self.style.SUCCESS('✓ Sample data created successfully!'))
        elif recent_invoices == 0:
            self.stdout.write(self.style.WARNING(
                '\n⚠️  No invoices in the last 30 days!'
            ))
            self.stdout.write('Run with --seed flag to create sample data:')
            self.stdout.write('  python manage.py check_vehicle_tracking_data --seed')

        # Show sample invoices
        if recent_invoices > 0:
            self.stdout.write('\n=== Sample Recent Invoices ===')
            invoices = Invoice.objects.filter(
                invoice_date__range=[thirty_days_ago, today]
            ).order_by('-invoice_date')[:5]

            for inv in invoices:
                self.stdout.write(
                    f"  Invoice: {inv.invoice_number} | "
                    f"Date: {inv.invoice_date} | "
                    f"Vehicle: {inv.vehicle.plate_number if inv.vehicle else 'None'} | "
                    f"Amount: {inv.total_amount}"
                )

    def seed_sample_data(self):
        """Create sample invoices with vehicles for testing"""
        # Ensure we have a branch
        branch, _ = Branch.objects.get_or_create(
            code='DEFAULT',
            defaults={'name': 'Default Branch', 'region': 'Main'}
        )

        # Create or get customers
        customers = []
        for i in range(3):
            customer, _ = Customer.objects.get_or_create(
                phone=f'+2557012345{70+i}',
                defaults={
                    'full_name': f'Test Customer {i+1}',
                    'email': f'customer{i+1}@test.com',
                    'branch': branch,
                    'address': f'Test Address {i+1}'
                }
            )
            customers.append(customer)

        # Create vehicles
        vehicles = []
        plates = ['TAA123', 'UBB456', 'ECC789']
        makes = ['Toyota', 'Nissan', 'Mitsubishi']
        models = ['Corolla', 'Sunny', 'Lancer']

        for i, customer in enumerate(customers):
            vehicle, _ = Vehicle.objects.get_or_create(
                customer=customer,
                plate_number=plates[i],
                defaults={
                    'make': makes[i],
                    'model': models[i],
                    'vehicle_type': 'Sedan'
                }
            )
            vehicles.append(vehicle)

        # Create invoices for the last 25 days
        today = timezone.now().date()
        for day_offset in range(1, 26, 8):  # Every 8 days
            invoice_date = today - timedelta(days=day_offset)

            for vehicle in vehicles:
                invoice, created = Invoice.objects.get_or_create(
                    invoice_number=f"INV-{vehicle.plate_number}-{invoice_date.isoformat()}",
                    defaults={
                        'branch': branch,
                        'customer': vehicle.customer,
                        'vehicle': vehicle,
                        'invoice_date': invoice_date,
                        'reference': vehicle.plate_number,
                        'subtotal': Decimal('50000'),
                        'tax_amount': Decimal('5000'),
                        'tax_rate': Decimal('10'),
                        'total_amount': Decimal('55000'),
                        'status': 'issued'
                    }
                )

                if created:
                    # Create a line item
                    InvoiceLineItem.objects.create(
                        invoice=invoice,
                        description=f'Service for {vehicle.make} {vehicle.model}',
                        quantity=Decimal('1'),
                        unit_price=Decimal('50000'),
                        line_total=Decimal('50000'),
                        tax_rate=Decimal('10'),
                        tax_amount=Decimal('5000'),
                        order_type='service'
                    )

                    # Create corresponding order
                    Order.objects.get_or_create(
                        customer=vehicle.customer,
                        vehicle=vehicle,
                        created_at=timezone.make_aware(timezone.datetime.combine(invoice_date, timezone.datetime.min.time())),
                        defaults={
                            'branch': branch,
                            'type': 'service',
                            'status': 'completed',
                            'priority': 'medium',
                            'description': f'Service order for {vehicle.plate_number}'
                        }
                    )
