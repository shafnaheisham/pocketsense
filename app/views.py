from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Expense,Student,Settlement,Group,ExpenseSplit
from .serializers import ExpenseSerializer,GroupSerializer,SettlementSerializer,ExpenseSplitSerializer,StudentSerializer
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated,AllowAny
from django.contrib.auth.models import User
from django.shortcuts import render,redirect
from django.contrib.auth import authenticate,login
from django.contrib.auth import logout
from datetime import timedelta
from django.core.mail import send_mail
from rest_framework.throttling import UserRateThrottle


class loginpageView(APIView):
    permission_classes = [AllowAny] 
    def get(self, request, *args, **kwargs):
        return render(request,'login.html')

class UserLogoutAPIView(APIView):
    def post(self, request, *args, **kwargs):
        
        logout(request)  
        return redirect('login.html')  
        
class LoginView(APIView):
    permission_classes = [AllowAny] 
    throttle_classes = [UserRateThrottle]
    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
       
        # Check if both username and password are provided
        if not username or not password:
            return render(request,'login.html',{"message": "Username and password are required."}, status=status.HTTP_400_BAD_REQUEST)

        # Authenticate user
        user = authenticate(username=username, password=password)
        
       
        if user is not None:
            login(request, user)
            return render(request,'student_viewexpenses.html',{"message": "Login successful.", "username": user.username,"stud_id":user.id},
                          status=status.HTTP_200_OK)
        else:
            # Return error if authentication fails
           return render(request,'login.html',{"message": "Invalid username or password."}, 
                         status=status.HTTP_401_UNAUTHORIZED)

def send_verification_email(request, user):
    subject = "Verify Your College Email"
    message = f"Hi Click the link to verify your email: "
    
    send_mail(subject, message, "admin@college.com", [user.email])

class StudentRegistrationAPIView(APIView):
    permission_classes = [AllowAny] 
    
    def get(self, request):
        
         return render(request,'studentregister.html')
        
    def post(self, request):
        #fullname=request.data.get("fullname")
        username = request.data.get("username")
        password = request.data.get("password")
        email = request.data.get("email")
        college = request.data.get("college")
        semester = request.data.get("semester")
        default_payment_method = request.data.get("default_payment_method")

        if not username or not password:
            return render(request,'studentregister.html',{"message": "Username and password are required."},
                          status=status.HTTP_400_BAD_REQUEST)

        if Student.objects.filter(username=username).exists():
           return render(request,'studentregister.html',{"message": "Username already exists."},
                         status=status.HTTP_400_BAD_REQUEST)

        
        if not email.endswith("@college.edu"):
            return render(request,'studentregister.html',{"message":"Only college emails are allowed."})
        user={
            'username':username,
            'password':password, 
            'email':email,
            'college':college,
            'semester':semester,
            'default_payment_methods':default_payment_method
        }
        serializer=StudentSerializer(data=user)   
        if serializer.is_valid:
            serializer.save()
             
        send_verification_email(request, user)
        
        return render(request,'studentregister.html',{"message": "Student registered successfully."},
                      status=status.HTTP_201_CREATED)
       
class ExpenseAPIView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        student_id = request.GET.get("stud_id")
        month = request.GET.get("month")
        category = request.GET.get("category")

        # Fetch student group
        student_group = Group.objects.filter(members=student_id)  

        if not student_group.exists():
            return render(request, 'student_viewexpenses.html', {'message': "You are not assigned to any group."})

        # Save student ID in session
        if student_id:
            request.session["stud_id"] = student_id
            request.session.modified = True 

        if not student_id:
            return render(request, 'student_viewexpenses.html', {"message": "Student ID is required."},
                          status=status.HTTP_400_BAD_REQUEST)

        # Search by month
        if month:
            try:
                month = int(month)
                if month < 1 or month > 12:
                    return render(request, 'student_viewexpenses.html',
                                  {"message": "Invalid month. Provide a value between 1 and 12."},
                                  status=status.HTTP_400_BAD_REQUEST)

                expenses = Expense.objects.filter(group__in=student_group, date__month=month)
                serializer = ExpenseSerializer(expenses, many=True)
                return render(request, 'student_viewexpenses.html', {'expenses': serializer.data},
                              status=status.HTTP_200_OK)

            except ValueError:
                return render(request, 'student_viewexpenses.html', {"Message": "Invalid month value."},
                              status=status.HTTP_400_BAD_REQUEST)

        # Search by category
        if category:
            expenses = Expense.objects.filter(group__in=student_group, category=category)
            serializer = ExpenseSerializer(expenses, many=True)
            return render(request, 'student_viewexpenses.html', {'expenses': serializer.data, "stud_id": student_id},
                          status=status.HTTP_200_OK)

        # Search by category and month
        if category and month:
            expenses = Expense.objects.filter(group__in=student_group, category=category, date__month=month)
            expenseserializer = ExpenseSerializer(expenses, many=True)
            return render(request, 'student_viewexpenses.html', {'expenses': expenseserializer.data, "stud_id": student_id},
                          status=status.HTTP_200_OK)

        # Fetch all expenses if no filters are applied
        expenses = Expense.objects.filter(group__in=student_group)
        serializer = ExpenseSerializer(expenses, many=True)
        return render(request, 'student_viewexpenses.html', {'expenses': serializer.data, "stud_id": student_id},
                      status=status.HTTP_200_OK)

    def post(self, request):
        print('hi add expense')
        student_id= request.session.get("stud_id")
        #student_id = request.data.get("stud_id")
        print(student_id)
        amount = request.data.get("amount")
        category = request.data.get("category")
        split_type = request.data.get("split_type")
        date = request.data.get("date")
        group = request.data.get("group")
        receipt_image = request.FILES.get("receipt_image")  # For handling file uploads
        payee = request.data.get("payee")
    
        try:
            student = Student.objects.get(id=student_id)
            if student:
                return render(request,'addexpenses.html')
        except Student.DoesNotExist:
            return render(request,'addexpenses.html',{"message": "Invalid student ID"},
                          status=status.HTTP_400_BAD_REQUEST)

        data = {
            "amount": amount,
            "category": category,
            "split_type": split_type,
            "date": date,
            "group": group,
            "created_by": student.id,}

   
        if receipt_image:
            data["receipt_image"] = receipt_image
        #Add expense
        serializer = ExpenseSerializer(data=data)
        if serializer.is_valid():
            expense = serializer.save()

        #Add data to ExpenseSplit
        if split_type == "equal" and group:
            # Fetch group members and create splits
            get_group=Group.objects.filter(members=student,name=group).values("id","name")
            if get_group:
                group_members = Group.objects.get(id=get_group.id).members.all()
            split_amount = float(amount) / len(group_members)
            for member in group_members:
                split_data={
                    'expense':expense,
                    'user':member,
                    'amount':split_amount}
                serializer = ExpenseSplitSerializer(data=data)
                if serializer.is_valid():
                    serializer.save()
                
        
        #Add data to settlement
        group_members = group.members.all()  
        payers = group_members.exclude(id=payee.id)
        for payer in payers:
            
            data={
                    'payer':payer,
                    'payee':payee,
                    'status':"Pending",  
                    'settlement_method':"Manual", 
                    'due_date':now() + timedelta(days=30),  # 1 month from expense creation
                    'expense':split_amount  
                }  
            serializer = SettlementSerializer(data=data)
            if serializer.is_valid():
                expense = serializer.save()
                
                return render(request,'addexpenses.html',{"message":"Expense created"}, status=status.HTTP_201_CREATED)
        return render(request,'addexpenses.html',{"message":"Invalid data cannot create expense"}, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        expense_id = request.data.get("id")
        expense = Expense.objects.filter(
                            id=expense_id)
        serializer = ExpenseSerializer(expense, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return render(request,'addexpenses.html',{"message":serializer.data}, status=status.HTTP_200_OK)
        return render(request,'addexpenses.html',{"message":serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        
        expense = Expense.objects.get( user=request.stud)
        expense.delete()
        return render(request,'addexpenses.html',{"message": "Expense deleted successfully"}, status=status.HTTP_204_NO_CONTENT)


class CreateGroupAPIView(APIView):
    
    permission_classes = [IsAuthenticated]
    def post(self,request):
        data=request.data
        print(data)
        name=request.data.get('name')
        members=request.data.get('members')
        description=request.data.get('description')
        stud_id=6
        grdata={'name':name,
                'members':members,
                'description':description,
                'created_by':stud_id
                }
        serializer =GroupSerializer (data=grdata)
        
        if serializer.is_valid():
            print(serializer)
            serializer.save()  # Attach the logged-in user
            return render(request,'creategroup.html',{'message':'Following group created:'+serializer.data}, status=status.HTTP_201_CREATED)
        
        return render(request,'creategroup.html',{'message':"Invalid data"}, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        try:
            group = Group.object.get(name=request.data['name'])
        except Group.DoesNotExist:
           return render(request,'creategroup.html',{'message': "Group not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = GroupSerializer(group, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return render(request,'creategroup.html',{'message':'Group Updated'}, status=status.HTTP_200_OK)
        return render(request,'creategroup.html',{'message':serializer.errors}, status=status.HTTP_400_BAD_REQUEST)  
    
    def delete(self, request):
        # Delete a franchisee type
        try:
            group = Group.object.get(name=request.data['name'])
        except Group.DoesNotExist:
           return render(request,'creategroup.html',{'message': "Group not found"}, status=status.HTTP_404_NOT_FOUND)


        group.delete()
        return render(request,'creategroup.html',{"message": " Group deleted successfully"}, status=status.HTTP_204_NO_CONTENT)




from django.db.models import Sum
from django.utils.timezone import now
import calendar
import json

def Spending_analysis(request):
    student = 6  
    student_groups = Group.objects.filter(members=student)  # Get groups where student is a member

    
    selected_month = int(request.GET.get("month", now().month))  
    selected_year = int(request.GET.get("year", now().year))  

    
    monthly_spending = (
        Expense.objects.filter(
            group__in=student_groups,
            date__year=selected_year,
            date__month=selected_month
        )
        .values('category')
        .annotate(total_spent=Sum('amount'))
    )

    categories = [item['category'] for item in monthly_spending]
    spending = [float(item['total_spent']) for item in monthly_spending]  # Convert Decimal to float

    
    group_spending_data = (
        Expense.objects.filter(
            group__in=student_groups,
            date__year=selected_year,
            date__month=selected_month
        )
        .values('group__name')  
        .annotate(total_spent=Sum('amount'))
    )

    group_names = [item['group__name'] for item in group_spending_data]
    group_spending = [float(item['total_spent']) for item in group_spending_data]  # Convert Decimal to float

    
    months = [{"num": i, "name": calendar.month_name[i]} for i in range(1, 13)]
    print(group_names)
    print(group_spending)
    context = {
        'selected_month': selected_month,
        'selected_year': selected_year,
        'months': months,  # Month dropdown options
        'current_month_name': calendar.month_name[selected_month],
        'categories': json.dumps(categories),  
        'spending': json.dumps(spending),  
        'group_names': json.dumps(group_names),
        'group_spending': json.dumps(group_spending),
    }

    return render(request, 'spending_analysis.html', context)
