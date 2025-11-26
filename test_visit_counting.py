"""
Test to verify that visit counting works correctly when creating customers and orders.
This validates the fix for the issue where creating a customer and one order showed 2 visits instead of 1.
"""

import os
import django
from django.test import TestCase
from django.contrib.auth.models import User

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pos_tracker.settings')
django.setup()

from tracker.models import Customer, Branch, Order
from tracker.services import CustomerService, OrderService


class VisitCountingTestCase(TestCase):
    """Test cases for customer visit counting logic"""
    
    def setUp(self):
        """Set up test data"""
        self.branch = Branch.objects.create(name='Test Branch', code='TB')
        self.user = User.objects.create_user(username='testuser', password='pass123')
    
    def test_customer_creation_does_not_increment_visits(self):
        """When creating a customer, total_visits should be 0"""
        customer, created = CustomerService.create_or_get_customer(
            branch=self.branch,
            full_name='John Doe',
            phone='555-1234',
            customer_type='personal'
        )
        
        self.assertTrue(created, "Customer should be newly created")
        self.assertEqual(customer.total_visits, 0, "New customer should have 0 visits")
        self.assertIsNone(customer.last_visit, "New customer should have no last_visit")
    
    def test_first_order_increments_visit_count(self):
        """When creating the first order for a customer, total_visits should be 1"""
        customer, _ = CustomerService.create_or_get_customer(
            branch=self.branch,
            full_name='Jane Smith',
            phone='555-5678',
            customer_type='personal'
        )
        
        # Verify initial state
        self.assertEqual(customer.total_visits, 0, "Initial visits should be 0")
        
        # Create first order
        order = OrderService.create_order(
            customer=customer,
            order_type='service',
            branch=self.branch,
            description='Test service order'
        )
        
        # Refresh customer from DB to get updated values
        customer.refresh_from_db()
        
        self.assertEqual(customer.total_visits, 1, "After first order, visits should be 1")
        self.assertIsNotNone(customer.last_visit, "After first order, last_visit should be set")
    
    def test_second_order_increments_visit_count(self):
        """When creating a second order, total_visits should be 2"""
        customer, _ = CustomerService.create_or_get_customer(
            branch=self.branch,
            full_name='Bob Johnson',
            phone='555-9999',
            customer_type='personal'
        )
        
        # Create first order
        OrderService.create_order(
            customer=customer,
            order_type='service',
            branch=self.branch
        )
        
        # Refresh and check
        customer.refresh_from_db()
        first_visit_count = customer.total_visits
        
        # Create second order
        OrderService.create_order(
            customer=customer,
            order_type='sales',
            branch=self.branch,
            item_name='Tire',
            brand='Michelin',
            quantity=4
        )
        
        # Refresh and check
        customer.refresh_from_db()
        
        self.assertEqual(customer.total_visits, 2, "After second order, visits should be 2")
        self.assertEqual(first_visit_count + 1, customer.total_visits, "Visits should increment by 1")
    
    def test_existing_customer_preserves_visit_count(self):
        """Getting an existing customer should NOT increment visit count"""
        # Create customer first time
        customer1, created1 = CustomerService.create_or_get_customer(
            branch=self.branch,
            full_name='Alice Brown',
            phone='555-1111',
            customer_type='personal'
        )
        
        # Create an order to set visit count to 1
        OrderService.create_order(
            customer=customer1,
            order_type='service',
            branch=self.branch
        )
        customer1.refresh_from_db()
        initial_visits = customer1.total_visits
        
        # Get the same customer again (without creating new order)
        customer2, created2 = CustomerService.create_or_get_customer(
            branch=self.branch,
            full_name='Alice Brown',
            phone='555-1111',
            customer_type='personal'
        )
        
        self.assertFalse(created2, "Customer should not be newly created")
        self.assertEqual(customer2.total_visits, initial_visits, "Visit count should not change when getting existing customer")
        self.assertEqual(customer1.id, customer2.id, "Should be the same customer")


def run_tests():
    """Run all tests"""
    import unittest
    
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(VisitCountingTestCase)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    exit(0 if success else 1)
