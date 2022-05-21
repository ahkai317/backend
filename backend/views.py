from django.http import HttpResponse, JsonResponse
# def get_ip(request):
#   x_forwarded_for = request.META.get('x-forwarded-for')
#   if x_forwarded_for:
#     ip = x_forwarded_for.split(',')[0]#所以這裏是真實的ip
#   else:
#     ip = request.META.get('REMOTE_ADDR')#這裏獲得代理ip
#   return HttpResponse(request.META.items())

# -*- coding: utf-8 -*-
"""
Created on Tue Apr 26 03:29:13 2022

@author: Zentropy 
"""

from datetime import timedelta
from backend.serializers import LogOutSerializer
from rest_framework import status
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated


def stock_data(request):
    """
    參數１：台股代號。
    參數２：開查詢時間（開始）。格式：yyyy-mm-dd。
    參數３：開查詢時間（結束）。格式：yyyy-mm-dd。

    範例：
    splitData=stock_data("2330","2016-01-01","2022-12-31")
    """
    import yfinance as yf
    from datetime import datetime
    res = request.GET
    stock = res['code']
    start = res['start']
    end = datetime.strptime(res['end'], "%Y-%m-%d") + timedelta(days=1)

    df = yf.download(stock+".TW", start=start, end=end.strftime("%Y-%m-%d"))
    del df["Adj Close"]
    del df["Volume"]

    df.insert(0, "day", df.index.strftime("%Y-%m-%d"))
    df.insert(2, "close", df.Close)
    df.insert(3, "low", df.Low)

    del df["Close"]
    del df["Low"]

    df = df.iloc[:].round(2)
    stock_data = df.values.tolist()
    return JsonResponse(stock_data, safe=False)


class LogoutAPIView(generics.GenericAPIView):
    serializer_class = LogOutSerializer

    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({'detail': 'Logout succeed'}, status=status.HTTP_204_NO_CONTENT)

# class PerdictAPIView(generics.GenericAPIView):
