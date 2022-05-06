from rest_framework.serializers import ModelSerializer
from stock_name.models import StockName

class StockSerializer(ModelSerializer):
  class Meta:
    model = StockName
    fields = '__all__'

class StockIndustrySerializer(ModelSerializer):
  class Meta:
    model = StockName
    fields = ['industry']