import django_filters


class StockFilter(django_filters.rest_framework.FilterSet):
    stock = django_filters.CharFilter(
        field_name='stock__stock', lookup_expr='iexact')
    sort = django_filters.OrderingFilter(
        fields=['stock__stockName', '-stock__stock', 'stock__stock', 'stock__industry', '-stock__industry'])
    stockName = django_filters.CharFilter(
        field_name='stock__stockName', lookup_expr='icontains')
    industry = django_filters.CharFilter(
        field_name='stock__industry', lookup_expr='iexact')
