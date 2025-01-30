from rest_framework import serializers
from .models import Expense, ExpenseSplit, Group, Student,Settlement

class ExpenseSplitSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExpenseSplit
        fields = ['expense','user', 'amount']

class ExpenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Expense
        fields = [ 'amount', 'category', 'split_type', 'date', 'group', 'receipt_image','created_by']

    
class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields =['name','description','created_by','members']

class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields ='__all__'
class SettlementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Settlement
        fields = '__all__'
