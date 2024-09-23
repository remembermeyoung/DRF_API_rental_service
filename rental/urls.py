from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import BicycleDetailAPIView, BicycleStatusListAPIView, RegistrationAPIView, OrdersHistoryAPIView, \
    LogInAPIView, LogOutAPIView

urlpatterns = [
    path('registration/', RegistrationAPIView.as_view(), name='registration'),
    path('login/', LogInAPIView.as_view(), name='login'),
    path('logout/', LogOutAPIView.as_view(), name='logout'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('bicycle/<str:status>/', BicycleStatusListAPIView.as_view(), name='bicycle_list'), #all, free, rented
    path('bicycle/detail/<int:pk>/', BicycleDetailAPIView.as_view(), name='bicycle_detail'),
    path('history/', OrdersHistoryAPIView.as_view(), name='history'),
]
