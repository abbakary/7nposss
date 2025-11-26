from django.core.management.base import BaseCommand
from django.test import Client
from django.contrib.auth import get_user_model
from tracker.models import Customer, Branch, Order
from datetime import datetime
from decimal import Decimal
import json
import threading
import time

User = get_user_model()


class Command(BaseCommand):
    help = 'Test invoice upload functionality with database locking scenarios'

    def add_arguments(self, parser):
        parser.add_argument(
            '--concurrent',
            type=int,
            default=1,
            help='Number of concurrent upload threads to simulate'
        )
        parser.add_argument(
            '--order-id',
            type=int,
            help='Order ID to use for testing (will create one if not provided)'
        )

    def handle(self, *args, **options):
        concurrent_threads = options['concurrent']
        order_id = options['order_id']

        self.stdout.write(self.style.SUCCESS('\n=== INVOICE UPLOAD TEST ===\n'))

        # Get or create test user
        user, created = User.objects.get_or_create(
            username='test_uploader',
            defaults={
                'email': 'test_uploader@example.com',
                'is_staff': True,
                'is_superuser': False
            }
        )
        if created:
            user.set_password('testpass123')
            user.save()
            self.stdout.write(f"Created test user: {user.username}")

        # Get or create branch
        branch, _ = Branch.objects.get_or_create(
            code='TEST',
            defaults={'name': 'Test Branch', 'region': 'Test'}
        )

        # Get or create customer
        customer, created = Customer.objects.get_or_create(
            phone='+255700999999',
            defaults={
                'full_name': 'Test Customer',
                'email': 'testcustomer@example.com',
                'branch': branch
            }
        )

        # Get or create order
        if order_id:
            try:
                order = Order.objects.get(id=order_id)
            except Order.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'Order {order_id} not found'))
                return
        else:
            order, created = Order.objects.get_or_create(
                customer=customer,
                type='service',
                defaults={
                    'branch': branch,
                    'status': 'created',
                    'priority': 'medium'
                }
            )
            if created:
                self.stdout.write(f"Created test order: {order.id}")

        # Prepare invoice data
        invoice_data = {
            'customer_id': str(customer.id),
            'customer_name': customer.full_name,
            'customer_phone': customer.phone,
            'customer_email': customer.email,
            'customer_type': 'personal',
            'invoice_number': f'TEST-{datetime.now().timestamp()}',
            'invoice_date': datetime.now().strftime('%Y-%m-%d'),
            'subtotal': '5000',
            'tax_amount': '500',
            'total_amount': '5500',
            'tax_rate': '10',
            'selected_order_id': str(order.id),
            'item_description[]': ['Test Item 1', 'Test Item 2'],
            'item_code[]': ['TST001', 'TST002'],
            'item_qty[]': ['1', '2'],
            'item_price[]': ['2500', '1250'],
            'item_unit[]': ['PCS', 'PCS'],
            'item_value[]': ['2500', '2500'],
        }

        self.stdout.write(f"Test Setup:")
        self.stdout.write(f"  Customer: {customer.full_name} ({customer.id})")
        self.stdout.write(f"  Order: {order.id} ({order.type})")
        self.stdout.write(f"  Concurrent uploads: {concurrent_threads}\n")

        if concurrent_threads == 1:
            # Single upload test
            self.stdout.write("Running single upload test...")
            self._test_single_upload(user, invoice_data)
        else:
            # Concurrent upload test
            self.stdout.write(f"Running concurrent upload test with {concurrent_threads} threads...")
            self._test_concurrent_uploads(user, invoice_data, concurrent_threads)

        self.stdout.write(self.style.SUCCESS('\n✓ Test completed!\n'))

    def _test_single_upload(self, user, invoice_data):
        """Test single invoice upload"""
        client = Client()

        # Login
        login_ok = client.login(username=user.username, password='testpass123')
        if not login_ok:
            self.stdout.write(self.style.WARNING('Note: Login failed. This test requires authentication.'))
            return

        try:
            # Make POST request
            start_time = time.time()
            response = client.post(
                '/tracker/api/invoices/create-from-upload/',
                data=invoice_data
            )
            duration = time.time() - start_time

            result = response.json()
            if result.get('success'):
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Upload successful in {duration:.2f}s')
                )
                self.stdout.write(f"  Invoice ID: {result.get('invoice_id')}")
                self.stdout.write(f"  Invoice Number: {result.get('invoice_number')}")
            else:
                self.stdout.write(
                    self.style.ERROR(f'✗ Upload failed: {result.get("message")}')
                )
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'✗ Error: {e}'))

    def _test_concurrent_uploads(self, user, invoice_data, num_threads):
        """Test concurrent invoice uploads"""
        results = {'success': 0, 'failed': 0, 'errors': []}
        lock = threading.Lock()

        def upload_in_thread(thread_id):
            client = Client()
            login_ok = client.login(username=user.username, password='testpass123')
            if not login_ok:
                return

            try:
                # Modify invoice number to make it unique
                data = invoice_data.copy()
                data['invoice_number'] = f"TEST-{thread_id}-{time.time()}"

                start_time = time.time()
                response = client.post(
                    '/tracker/api/invoices/create-from-upload/',
                    data=data
                )
                duration = time.time() - start_time

                result = response.json()
                with lock:
                    if result.get('success'):
                        results['success'] += 1
                        self.stdout.write(
                            self.style.SUCCESS(f'  Thread {thread_id}: ✓ Success ({duration:.2f}s)')
                        )
                    else:
                        results['failed'] += 1
                        error = result.get('message', 'Unknown error')
                        self.stdout.write(
                            self.style.ERROR(f'  Thread {thread_id}: ✗ Failed - {error}')
                        )
                        results['errors'].append(error)
            except Exception as e:
                with lock:
                    results['failed'] += 1
                    self.stdout.write(self.style.ERROR(f'  Thread {thread_id}: ✗ Exception - {e}'))
                    results['errors'].append(str(e))

        # Start all threads
        threads = []
        start_time = time.time()
        for i in range(num_threads):
            t = threading.Thread(target=upload_in_thread, args=(i,))
            threads.append(t)
            t.start()
            time.sleep(0.1)  # Stagger thread starts slightly

        # Wait for all threads
        for t in threads:
            t.join()

        total_duration = time.time() - start_time

        # Print summary
        self.stdout.write(f"\nResults:")
        self.stdout.write(f"  Success: {results['success']}")
        self.stdout.write(f"  Failed: {results['failed']}")
        self.stdout.write(f"  Total time: {total_duration:.2f}s")

        if results['errors']:
            self.stdout.write(f"\nErrors encountered:")
            for error in set(results['errors']):
                self.stdout.write(f"  - {error}")
