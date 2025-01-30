from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.hashers import make_password


class Student(AbstractUser):
    college = models.CharField(max_length=100, null=True, blank=True)
    semester = models.IntegerField(null=True, blank=True)
    default_payment_methods = models.CharField(max_length=50, null=True, blank=True)

   
    def save(self, *args, **kwargs):
    #       # Hash the password if it is not already hashed
        if self.pk is None or not self.password.startswith('pbkdf2_sha256$'):
            self.password = make_password(self.password)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.username

class Group(models.Model):
    GROUP_CHOICES= [
        ("hostel_roommates","Hostel Roomamtes"),
        ("project_teams","Project Team"),
        ("trip_groups","Trip Group"),
        ("other","Other"),]
    name = models.CharField(max_length=100,choices=GROUP_CHOICES)
    description = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey('app.Student', on_delete=models.CASCADE, related_name="created_groups")
    members = models.ManyToManyField(Student, related_name="expense_groups")

    def __str__(self):
        return self.name



class Expense(models.Model):
    SPLIT_CHOICES = [
        ("equal", "Equal"),
        ("percentage", "Percentage"),
        ("custom", "Custom"),
    ]
    
    CATEGORY_CHOICES = [
        ('food', 'Food'),
        ('travel', 'Travel'),
        ('academics', 'Academics'),
        ('entertainment', 'Entertainment'),
    ]

    amount = models.DecimalField(max_digits=10, decimal_places=2)
    category =models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    split_type = models.CharField(max_length=20, choices=SPLIT_CHOICES, default="equal")
    date = models.DateField(auto_now_add=True)
    receipt_image = models.ImageField(upload_to="receipts/", blank=True, null=True)
    created_by = models.ForeignKey('app.Student', on_delete=models.CASCADE, related_name="expenses")
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name="expenses", null=True, blank=True)

    def __str__(self):
        return f"Expense {self.id} - {self.amount} ({self.category})"


class ExpenseSplit(models.Model):
    expense = models.ForeignKey(Expense, on_delete=models.CASCADE, related_name="splits")
    user = models.ForeignKey('app.Student', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.user.username} owes {self.amount} for Expense {self.expense.id}"

class Settlement(models.Model):
    payer = models.ForeignKey('app.Student', on_delete=models.CASCADE, related_name="settlements_made")
    payee = models.ForeignKey('app.Student', on_delete=models.CASCADE, related_name="settlements_received")
    payment_status = models.CharField(
        max_length=20,
        choices=[('pending', 'Pending'), ('completed', 'Completed')],
        default='pending'
    )
    settlement_method = models.CharField(max_length=50, blank=True, null=True)
    due_date = models.DateField(null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Settlement: {self.payer.username} to {self.payee.username} ({self.payment_status})"
