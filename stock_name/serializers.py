from statistics import mode
from attr import field
from numpy import source
from stock_name.models import StockDetail, StockName
from rest_framework.serializers import ModelSerializer, RelatedField
from rest_framework.pagination import PageNumberPagination


class StockIndustrySerializer(ModelSerializer):
    class Meta:
        model = StockName
        fields = ['industry']

# =====================================


class StockSerializer(ModelSerializer):
    class Meta:
        model = StockName
        fields = ['stock', 'stockName', 'industry',
                  'updated']


class StockDetailSerializer(ModelSerializer):
    stock = StockSerializer(many=False)

    class Meta:
        model = StockDetail
        fields = "__all__"


# =====================================


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 30
    page_size_query_param = 'page_size'
    max_page_size = 100


# =====================================
# class StockOrderSerializer(ModelSerializer):
#     class Meta:
#         model = StockName
#         fields = ['stock', 'stockName', 'industry',
#                   'updated']


# class StockDetailOrderSerializer(ModelSerializer):
#     stock = StockOrderSerializer(many=False)

#     class Meta:
#         model = StockDetail
#         fields = "__all__"

# =====================================
