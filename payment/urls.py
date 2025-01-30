from django.urls import path, include

from .views import CreatePaymentView, CreatePaymentPostView, VerifyPaymentView, PaymentSuccessView
urlpatterns = [
    path('login/expenses/payment/create-payment/', CreatePaymentView.as_view(), name='create_payment'),
    path('create-payment-post/', CreatePaymentPostView.as_view(), name='create_payment_post'),
    path('verify-payment/', VerifyPaymentView.as_view(), name='verify_payment'),
    path('payment/payment-success/', PaymentSuccessView.as_view(), name='payment_success'),
    
]