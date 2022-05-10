from rest_framework.response import Response
from stock_name.models import StockName
from stock_name.serializers import StockSerializer, StockIndustrySerializer
from rest_framework.viewsets import ReadOnlyModelViewSet
from django_filters.rest_framework import DjangoFilterBackend
from stock_name.filter import StockFilter
from rest_framework import filters
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
# Create your views here.


class StockViewSet(ReadOnlyModelViewSet):
    queryset = StockName.objects.all()
    serializer_class = StockSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filter_class = StockFilter
    search_fields = ['^stock', '^stockName']
    permission_classes = [AllowAny]

    @action(detail=False, methods=['get'])
    def search(self, request):
        queryset = super().filter_queryset(self.queryset)[:10]
        serializer = StockSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def industry(self, request):
        queryset = StockName.objects.values(
            'industry').distinct().order_by('industry')
        serializer = StockIndustrySerializer(queryset, many=True)
        return Response(serializer.data)

# def showStockName(request):
#   res = request.GET
#   stockList = StockName.objects.filter(Q(stock__startswith=res['stock']) | Q(stockName__startswith=res['stock'])).order_by('stock')[:10]
#   result = list(stockList.values("stock", "stockName", "updated"))
#   return JsonResponse(result, safe=False)
