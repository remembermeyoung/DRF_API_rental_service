from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework.routers import DefaultRouter
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from .views import BicycleViewSet, OrdersViewSet

router_v2 = DefaultRouter()

router_v2.register('bicycle', BicycleViewSet, basename='bicycle')
router_v2.register('orders', OrdersViewSet, basename='orders')

urlpatterns = [
    path('', include(router_v2.urls)),
    path('auth/', include('djoser.urls')),
    path('token/', TokenObtainPairView.as_view(), name='token_get'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]

schema_view = get_schema_view(
   openapi.Info(
      title='Rental API',
      default_version='v2',
      description='Test description',
      license=openapi.License(name='BSD License'),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns += [path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui')]
