# from django.shortcuts import render
import os
import sys
import django
sys.path.append("/app/backend/") 
os.environ['DJANGO_SETTINGS_MODULE'] = 'backend.settings'
django.setup()

from stock_name.models import StockName
def get_stock_name():
    import requests,json
    
    url="https://www.twse.com.tw/exchangeReport/MI_INDEX?response=json&date=&type=ALLBUT0999&_="
    headers={
            "Content-Type":"application/json",
            "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36"
        }
    response=requests.get(url,headers=headers)
    data=json.loads(response.text)
    stockData = []
    datas = data['data9']
    for i in datas:
        StockName.objects.update_or_create(defaults={'stock': i[0], 'stockName': i[1]}, stock=i[0], stockName=i[1])
        # data_info = []
        # data_info.append(i[0])
        # data_info.append(i[1])
        # stockData.append(data_info)
get_stock_name()