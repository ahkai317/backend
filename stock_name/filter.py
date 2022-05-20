from email.policy import default
import django_filters
from sympy import false

from stock_name.models import StockDetail, StockName


class StockFilter(django_filters.rest_framework.FilterSet):
    def __init__(self, data=None, *args, **kwargs):
        if 'stocks' in data:
            if not data['stocks']:
                kwargs['queryset'] = kwargs['queryset'].none()
        if "industry" in data:
            if not data['industry']:
                data = data.copy()  # or data._mutable=True 因為預設是不能修改的
                data = {"industry": "化學工業"}
        super(StockFilter, self).__init__(data, *args, **kwargs)

    stock = django_filters.CharFilter(
        field_name='stock__stock', lookup_expr='iexact')
    stocks = django_filters.BaseInFilter(
        field_name='stock__stock', lookup_expr='in')
    sort = django_filters.OrderingFilter(
        fields=['stock__stockName', '-stock__stock', 'stock__stock', 'stock__industry', '-stock__industry'])
    stockName = django_filters.CharFilter(
        field_name='stock__stockName', lookup_expr='icontains')
    industry = django_filters.CharFilter(
        field_name='stock__industry', lookup_expr='iexact')

    class Meta:
        model = StockDetail
        fields = "__all__"
