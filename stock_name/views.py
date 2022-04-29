from django.shortcuts import render
from stock_name.models import StockName
from django.http import JsonResponse
from django.db.models import Q
# Create your views here.

def showStockName(request):
  res = request.GET
  stockList = StockName.objects.filter(Q(stock__startswith=res['stock']) | Q(stockName__startswith=res['stock'])).order_by('stock')[:10]
  result = list(stockList.values("stock", "stockName"))
  return JsonResponse(result, safe=False)