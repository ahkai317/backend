from django.contrib import admin
from django.urls import include, path
from . views import main, stock_data
from stock_name.views import showStockName

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include('djoser.urls')),
    path('api/v1/', include('djoser.urls.jwt')),
    
    path('stock/', main),
    path('stock_data/', stock_data),
    path('stock_name/', showStockName)
]
