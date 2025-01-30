from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import ExpenseAPIView,StudentRegistrationAPIView,LoginView,loginpageView,CreateGroupAPIView,Spending_analysis

urlpatterns = [
    
    path('',loginpageView.as_view(),name='loginpage'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/',loginpageView.as_view(),name='logout'),
    path('login/expenses/', ExpenseAPIView.as_view(), name='expenses'),
    path('expenses/<int:stud_id>/', ExpenseAPIView.as_view(), name='expense-detail'),
    path('studentregister/', StudentRegistrationAPIView.as_view(), name='studentregister'),
    path('creategroup/',CreateGroupAPIView.as_view(),name='creategroup'),
    path('spending-analysis/', Spending_analysis, name='spending-analysis'),
    
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
