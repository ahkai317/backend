from django.contrib import admin
from stock_name.models import StockDetail, StockName
from django.contrib.admin.options import ModelAdmin
# Register your models here.


class StockAdmin(ModelAdmin):
    list_per_page = 30
    list_display = ('stock', 'stockName', 'industry', 'updated')
    search_fields = ('stock', 'stockName', 'industry')
    readonly_fields = ('updated',)

    filter_horizontal = ()
    list_filter = ('industry',)
    fieldsets = ()


admin.site.register(StockName, StockAdmin)


class StockAdmins(ModelAdmin):
    list_per_page = 30
    list_display = [f.name for f in StockDetail._meta.fields]
    search_fields = ('stock__stock',)
    readonly_fields = ('updated',)

    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()


admin.site.register(StockDetail, StockAdmins)
