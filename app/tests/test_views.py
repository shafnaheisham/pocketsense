from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from app.models import Student, Expense, Group  # Adjust based on your models

class TestViews(TestCase):
    def setUp(self):
        self.client = APIClient()  # DRF's test client

        # Sample data for requests
        self.student_data = {
            "username": "teststudent",
            "email": "test@student.com",
            "password": "testpass123"
        }

        self.expense_data = {
            "name": "Lunch",
            "amount": 20.50
        }

        self.group_data = {
            "name": "Study Group"
        }

    def test_student_registration(self):
        """Test student registration API"""
        url = reverse('studentregister')  # Adjust based on your URL name
        response = self.client.post(url, self.student_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_expense_creation(self):
        """Test expense creation API"""
        url = reverse('expenses')  # Adjust based on your URL name
        response = self.client.post(url, self.expense_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_group(self):
        """Test group creation API"""
        url = reverse('creategroup')  # Adjust based on your URL name
        response = self.client.post(url, self.group_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_get_expenses(self):
        """Test fetching expense list"""
        url = reverse('expenses')  # Adjust based on your URL name
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
