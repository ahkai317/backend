from statistics import mode
from attr import field
from numpy import source
from rest_framework.serializers import ModelSerializer, RelatedField
from stock_name.models import StockDetail, StockName


class StockIndustrySerializer(ModelSerializer):
    class Meta:
        model = StockName
        fields = ['industry']


class StockDetailSerializer(ModelSerializer):

    class Meta:
        model = StockDetail
        fields = "__all__"


class StockSerializer(ModelSerializer):
    stockDetail = StockDetailSerializer(many=True)

    class Meta:
        model = StockName
        fields = ['stock', 'stockName', 'industry',
                  'updated', 'stockDetail']
