from django.contrib import admin

from django.urls import include, path
from . views import main, stock_data

from rest_framework.routers import DefaultRouter

from user_info.views import UserModelViewSet
from stock_name.views import StockViewSet, news
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView
)
router = DefaultRouter()
router.register(r'user', UserModelViewSet)
router.register(r'stock_name', StockViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),

    path('stock/', main),
    path('stock_data/', stock_data),
    path('api/news/', news),

    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
