from rest_framework.serializers import ModelSerializer
from stock_name.models import StockName

class StockSerializer(ModelSerializer):
  class Meta:
    model = StockName
    fields = ['stock', 'stockName', 'industry', 'updated']

class StockIndustrySerializer(ModelSerializer):
  class Meta:
    model = StockName
    fields = ['industry']