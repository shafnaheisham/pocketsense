from django.test import TestCase

from django.urls import reverse,resolve
from app.views import StudentRegistrationAPIView,ExpenseAPIView,CreateGroupAPIView

class TestUrls(TestCase):
    def test_studreg_url(self):
        url=reverse('studentregister')
        self.assertEquals(resolve(url).func.view_class,StudentRegistrationAPIView)
    
    def test_expense_url(self):
        url=reverse('expenses')
        self.assertEquals(resolve(url).func.view_class,ExpenseAPIView)
    
    def test_groups_url(self):
        url=reverse('creategroup')
        self.assertEquals(resolve(url).func.view_class,CreateGroupAPIView)    
        
            
        