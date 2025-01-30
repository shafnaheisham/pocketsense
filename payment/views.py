from django.views.decorators.csrf import csrf_exempt
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import HttpResponse

from django.shortcuts import render, redirect
from django.http import JsonResponse
import razorpay
import json
from django.conf import settings
from django.db.models import Q
from app.models import Settlement,Expense,ExpenseSplit
from rest_framework.permissions import IsAuthenticated,AllowAny

RAZORPAY_KEY_ID="rzp_test_gdJRoszNsVfYHo"
RAZORPAY_KEY_SECRET="QPWGAgLd0Z3VsEQio5wLk10s"
razorpay_client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))


class CreatePaymentView(APIView):
    """
    Display the payment creation form.
    """
    permission_classes = [AllowAny] 
    def get(self, request, *args, **kwargs):
        #expense_id=request.data('id')
        expense_id=3
        payment_details=ExpenseSplit.objects.filter(expense_id=expense_id).first()
        print(payment_details.amount)
        return render(request, 'makepayment.html',{'amount_topay':payment_details.amount})



class CreatePaymentPostView(APIView):
    
    def post(self, request, *args, **kwargs):
        settlement_id = request.data.get('id')

        if not settlement_id:
            return render(request, 'payment/error.html', {"message": "Please enter an invoice ID."})

        try:
            settlement = Settlement.objects.get(
                Q(id=id) & 
                Q(payment_status__in=['pending']))
            
            amount = float(settlement.amount)
            order = razorpay_client.order.create({
                'amount': int(amount * 100),  # Razorpay expects amount in paise
                'currency': 'INR',
                'payment_capture': '1'
            })

            context = {
                'id': settlement.id,
                'amount': amount,
                'order_id': order['id'],
                'razorpay_key': settings.RAZORPAY_KEY_ID,
                'payer': settlement.sender.payer,
                'payee': settlement.sender.payee,
                
            }

            return render(request, "makepayment.html", context)

        except Settlement.DoesNotExist:
             return JsonResponse({"error": "Settlement with the provided ID does not exist."}, status=404)


class VerifyPaymentView(APIView):
    permission_classes = [AllowAny] 
    def post(self, request, *args, **kwargs):
        try:
            data = request.data
            required_fields = ['transaction_id', 'order_id', 'signature', 'payer','payee', 'amount']
            if not all(field in data for field in required_fields):
                 return JsonResponse({"message": "Missing required fields."}, status=404) 

            transaction_id = data['transaction_id']
            order_id = data['order_id']
            signature = data['signature']
            payer = data['payer']
            payee=data['payee']
            amount = float(data['amount'])

            try:
                # Verify Razorpay signature
                razorpay_client.utility.verify_payment_signature({
                    'razorpay_order_id': order_id,
                    'razorpay_payment_id': transaction_id,
                    'razorpay_signature': signature
                })

                # Update Invoice and Save Payment
                settlement = Settlement.objects.get(id=id)
                
                settlement.payment_status = 'paid'
                settlement.save()

                return render(request, 'success.html', {
                    
                    'transaction_id': transaction_id,
                    'amount_paid': amount
                })

            

            except razorpay.errors.SignatureVerificationError as e:
                return render(request, 'payment_success.html', {
                    "message": f"Signature verification failed: {str(e)}"
                })

        except json.JSONDecodeError:
            return render(request, 'payment_success.html', {"message": "Invalid JSON format."})

        except Exception as e:
            return render(request, 'payment_success.html', {
                "message": f"Unexpected error occurred: {str(e)}"
            })



class PaymentSuccessView(APIView):  
    
    def get(self, request, *args, **kwargs):
        invoice_id = request.GET.get('invoice_id')  # Get invoice_id from the query string
        if not invoice_id:
            return HttpResponse("Invoice ID is missing.", status=400)

        return render(request, 'success.html', {'invoice_id': invoice_id})


