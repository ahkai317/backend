from django.http import JsonResponse
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
import joblib
import numpy as np
import pandas as pd
from datetime import timedelta
from rest_framework import status
from rest_framework import status
from rest_framework import generics
import machineLearning.stock_feature as s
from rest_framework.request import Request
from rest_framework.response import Response
from backend.serializers import LogOutSerializer
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


def predict(request: Request) -> JsonResponse:
    stock = request.GET.get('stock')
    try:
        total = pd.read_csv("/app/backend/machineLearning/total.csv")
        idx = total[total["stock"] == stock].iloc[0, -1]
        if idx == 2:
            return JsonResponse({'detail': "ETN is unpredictable"}, status=status.HTTP_400_BAD_REQUEST)
        model = joblib.load(
            f"/app/backend/machineLearning/pkl/model_{idx}.pkl")
        model2 = joblib.load(
            f"/app/backend/machineLearning/pkl/model_32.pkl")

        df = s.data(stock)
        if df.shape[0] == 0:
            return JsonResponse({'detail': f"stock {stock} is unpredictable"}, status=status.HTTP_400_BAD_REQUEST)
        X = np.array(df.iloc[-1, 4:-1]).reshape(1, -1)
        y = model.predict(X)[0]
        y2 = model2.predict(X)[0]
        return JsonResponse({'predict': {
            'single': str(y),
            'universal': str(y2)
        }}, status=status.HTTP_200_OK)
    except FileNotFoundError:
        return JsonResponse({'detail': 'file not found'}, status=status.HTTP_404_NOT_FOUND)
    except IndexError:
        return JsonResponse({'detail': 'stock not found'}, status=status.HTTP_404_NOT_FOUND)
