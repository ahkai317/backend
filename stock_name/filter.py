import django_filters


class StockFilter(django_filters.rest_framework.FilterSet):
    stock = django_filters.CharFilter(
        field_name='stock', lookup_expr='startswith')
    sort = django_filters.OrderingFilter(
        fields=['stockName', 'stockName', '-stock', 'stock', 'industry', '-industry', 'updated'])
    stockName = django_filters.CharFilter(
        field_name='stockName', lookup_expr='icontains')
    industry = django_filters.CharFilter(
        field_name='industry', lookup_expr='icontains')
