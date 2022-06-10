from user_info.serializers import FavoriteStockSerializer
from stock_name.models import StockDetail, StockName
from rest_framework import serializers
from rest_framework.pagination import LimitOffsetPagination


class StockIndustrySerializer(serializers.ModelSerializer):
    class Meta:
        model = StockName
        fields = ['industry']

# =====================================


class StockSerializer(serializers.ModelSerializer):
    favoriteStock = FavoriteStockSerializer(many=True)

    class Meta:
        model = StockName
        fields = ['stock', 'stockName', 'industry',
                  'updated', 'favoriteStock']


class StockDetailSerializer(serializers.ModelSerializer):
    stock = StockSerializer(many=False)

    class Meta:
        model = StockDetail
        fields = "__all__"


# =====================================


class StandardResultsSetPagination(LimitOffsetPagination):
    page_size_query_param = 'page_size'
    max_page_size = 100
    default_limit = 30


class StockVolumnSerializer(serializers.ModelSerializer):
    stock = serializers.SlugRelatedField(
        many=False,
        read_only=True,
        slug_field='stock'
    )

    class Meta:
        model = StockDetail
        fields = ['volumn', 'stock']

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
