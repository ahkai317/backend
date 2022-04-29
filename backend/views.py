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

import numpy as np
import joblib
import datetime
from datetime import timedelta
import json
from django.views.decorators.csrf import csrf_exempt

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

@csrf_exempt
def main(request):
  if request.method == "POST":
      model = joblib.load('/app/backend/stock_model_0426.pkl')
      stock = json.loads(request.body)
      stock = stock['stock']

      start = str(datetime.date.today() - datetime.timedelta(days=30))
      end = str(datetime.date.today())
      
      def data_before_analysis(stock, start, end):
          import yfinance as yf
          
          df = yf.download(stock+".TW", start, end)
          
          df["yesterday_open"]  = df["Open"].shift(1)
          df["yesterday_close"] = df["Close"].shift(1)        
          
          df["Vol_avg"] = df["Volume"].rolling(window=10).mean()        
          
          df["x0"] = df["Close"].shift(3)
          df["x1"] = df["Close"].shift(2)
          df["x2"] = df["Close"].shift(1)
          df["x3"] = df["Close"]
          
          df.dropna(inplace=True)

          return df
  
      
      def vol_check(df):
          def vol_check(row):
              if row["Volume"] > row["Vol_avg"]*1.2:
                  return "1"
              elif row["Vol_avg"]*0.8 <= row["Volume"] <= row["Vol_avg"]*1.2:
                  return "2"
              elif row["Volume"] < row["Vol_avg"]*0.8:
                  return "3"
              
          df["vol_check"] = df.apply(vol_check, axis=1)
          df.dropna(inplace=True)
  
      
      def k1_check(df):
          def k1_way(row):
              if row["Open"] < row["Close"]:
                  return "1"           
              elif row["Open"] > row["Close"]:
                  return "2"
              elif row["Open"] == row["Close"]:
                  return "3"
              
          def k1_long(row):
              if (row["High"] - row["Low"])/(row["yesterday_close"]*0.2) > 0.14:
                  return "1" 
              elif 0.06 <= (row["High"] - row["Low"])/(row["yesterday_close"]*0.2) <= 0.14:
                  return "2"
              elif (row["High"] - row["Low"])/(row["yesterday_close"]*0.2) < 0.06:
                  return "3"        
  
              
          def k1_pattern(row):
              if row["High"] == row["Low"]:
                  return "51"
              elif row["High"] != row["Low"]:
                  if abs(row["Open"] - row["Close"])/(row["High"] - row["Low"]) == 1:
                      return "11"
                  else:
                      pattern = ""
                      oc_max = max(row["Open"], row["Close"])
                      oc_min = min(row["Open"], row["Close"])
                      ratio  = (row["High"] - oc_max)/(row["High"] - row["Low"] - oc_max + oc_min)
                      if 0.5 <= abs(row["Open"] - row["Close"])/(row["High"] - row["Low"])  < 1:
                          pattern += "2"
                      elif 0 < abs(row["Open"] - row["Close"])/(row["High"] - row["Low"])  < 0.5:
                          pattern += "3"
                      elif abs(row["Open"] - row["Close"])/(row["High"] - row["Low"])  == 0:
                          pattern += "4"
                          
                      if ratio < 0.15:
                          pattern += "1"
                      elif 0.15 <= ratio < 0.3:
                          pattern += "2"
                      elif 0.3 <= ratio <= 0.7:
                          pattern += "3"
                      elif 0.7 < ratio <= 0.85:
                          pattern += "4"
                      elif ratio > 0.85:
                          pattern += "5"
                          
                  return pattern
                          
              return "0"   
            
          df["k1_way"] = df.apply(k1_way, axis = 1)
          df["k1_long"] = df.apply(k1_long, axis = 1)
          df["k1_pattern"] = df.apply(k1_pattern, axis = 1)
          df.dropna(inplace=True)


      def k2_check(df):
          def k2_pattern(row):
              if (row["yesterday_k1_long"] in ("1", "2")) and (row["k1_long"] in ("1", "2")):
                  if (row["yesterday_k1_pattern"] in ("11", "21", "22", "23", "24", "25")) and (row["k1_pattern"] in ("11", "21", "22", "23", "24", "25")):
                      if row["yesterday_close"]*0.995 <= row["Close"] <= row["yesterday_close"]*1.005:
                          if row["yesterday_k1_way"] == "2" and row["k1_way"] == "1":
                              return "11" # 多頭遭遇線
                          if row["yesterday_k1_way"] == "1" and row["k1_way"] == "2":
                              return "12" # 空頭遭遇線
                          
              if row["yesterday_k1_long"] in ("1", "2"):
                  if row["yesterday_k1_pattern"] in ("11", "21", "22", "23", "24", "25"):
                      oc_max = max(row["yesterday_open"], row["yesterday_close"])
                      oc_min = min(row["yesterday_open"], row["yesterday_close"])
                      if (oc_min < row["Open"] < oc_max) and (oc_min < row["Close"] < oc_max):
                          if row["yesterday_k1_way"] == "2" and row["k1_way"] in ("1", "3"):
                              return "21" # 多頭懷抱線
                          if row["yesterday_k1_way"] == "1" and row["k1_way"] in ("2", "3"):
                              return "22" # 空頭懷抱線
                                            
              if (row["yesterday_k1_long"] in ("1", "2")) and (row["k1_long"] in ("1", "2")):
                  if (row["yesterday_k1_pattern"] in ("11", "21", "22", "23", "24", "25")) and (row["k1_pattern"] in ("11", "21", "22", "23", "24", "25")):
                      oc_max = max(row["yesterday_open"], row["yesterday_close"])
                      oc_min = min(row["yesterday_open"], row["yesterday_close"])
                      if (oc_min < row["Close"] < oc_max) and not (oc_min < row["Open"] < oc_max):
                          if (row["Close"] - row["yesterday_close"])/(row["yesterday_open"] - row["yesterday_close"]) >= 0.5:
                              if row["yesterday_k1_way"] == "2" and row["k1_way"] == "1":
                                  return "31" # 多頭插入線
                              if row["yesterday_k1_way"] == "1" and row["k1_way"] == "2":
                                  return "32" # 空頭插入線                            
                      
              if row["k1_long"] in ("1", "2"):
                  if row["k1_pattern"] in ("11", "21", "22", "23", "24", "25"):
                      oc_max = max(row["Open"], row["Close"])
                      oc_min = min(row["Open"], row["Close"])
                      if (oc_min < row["yesterday_open"] < oc_max) and (oc_min < row["yesterday_close"] < oc_max):
                          if row["yesterday_k1_way"] in ("2", "3") and row["k1_way"] == "1":
                              return "41" # 多頭吞噬線
                          if row["yesterday_k1_way"] in ("1", "3") and row["k1_way"] == "2":
                              return "42" # 空頭吞噬線
                          
              return "0"
                      
          df["yesterday_k1_way"] = df["k1_way"].shift(1)
          df["yesterday_k1_long"] = df["k1_long"].shift(1)
          df["yesterday_k1_pattern"] = df["k1_pattern"].shift(1)
          df["k2_pattern"] = df.apply(k2_pattern, axis = 1)
          df.dropna(inplace=True)
          
          
      def cubicfunc(df):
          def lagrange(row):
              from scipy.interpolate import lagrange
              import sympy as sp
              
              X = [0, 1, 2, 3]
              Y = [row["x0"], row["x1"], row["x2"], row["x3"]]       
              
              l = lagrange(X,Y)  
              x = sp.symbols('x')
              f = sp.Function('f')(x)
              f = l[0] + l[1]*x + l[2]*x**2 + l[3]*x**3
              
              if len(l) == 3:
                  d2 = sp.diff(f, x, 2).subs(x, 97)
                  if d2 > 0:
                      if row["x3"] > row["x0"]:
                          return "311"
                      elif row["x3"] == row["x0"]:
                          return "312"
                      elif row["x3"] < row["x0"]:
                          return "313"
                  elif d2 < 0:
                      if row["x3"] > row["x0"]:
                          return "321"
                      elif row["x3"] == row["x0"]:
                          return "322"
                      elif row["x3"] < row["x0"]:
                          return "323"               
                  
              elif len(l) == 2:
                  d2 = sp.diff(f, x, 2)
                  if d2 > 0:
                      return "21"
                  elif d2 < 0:
                      return "22"
              
              elif len(l) == 1:
                  d1 = sp.diff(f, x, 1)
                  if d1 > 0:
                      return "11"
                  elif d1 < 0:
                      return "12"
              
              elif len(l) == 0:
                  return "00"
          
          df["cubic"] = df.apply(lagrange, axis =1)
      
      
      def df_clean(df):
          df.dropna(inplace=True)
          del df["Adj Close"]
          del df["yesterday_open"]
          del df["yesterday_close"]
          del df["Vol_avg"]
          del df["yesterday_k1_way"]
          del df["yesterday_k1_long"]
          del df["yesterday_k1_pattern"]
          del df["x0"]
          del df["x1"]
          del df["x2"]
          del df["x3"]
          
      
      def data(stock, start, end):
          df = data_before_analysis(stock, start, end)
          vol_check(df)
          k1_check(df)
          k2_check(df)
          cubicfunc(df)
          
          df_clean(df)
          
          return df
      
      
      X = np.array(data(stock, start, end).iloc[-1, :]).reshape(1,-1)
      y = model.predict(X)
      
      return JsonResponse(y[0], safe=False)
    
    
    