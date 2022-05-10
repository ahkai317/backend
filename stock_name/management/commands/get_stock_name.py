# ========= django setting required ===============
from django.core.management.base import BaseCommand
from backend import settings
import logging

# ============ main code ===========================
import pandas as pd
from stock_name.models import StockName
from datetime import datetime
import requests


class Command(BaseCommand):

    def handle(self, *args, **options):
        urls = ['https://isin.twse.com.tw/isin/class_main.jsp?owncode=&stockname=&isincode=&market=1&issuetype=1&industry_code=&Page=1&chklike=Y',
                'https://isin.twse.com.tw/isin/class_main.jsp?owncode=&stockname=&isincode=&market=1&issuetype=I&industry_code=&Page=1&chklike=Y',
                'https://isin.twse.com.tw/isin/class_main.jsp?owncode=&stockname=&isincode=&market=1&issuetype=I1&industry_code=&Page=1&chklike=Y',
                'https://isin.twse.com.tw/isin/class_main.jsp?owncode=&stockname=&isincode=&market=1&issuetype=A&industry_code=&Page=1&chklike=Y',
                'https://isin.twse.com.tw/isin/class_main.jsp?owncode=&stockname=&isincode=&market=1&issuetype=J&industry_code=&Page=1&chklike=Y',
                'https://isin.twse.com.tw/isin/class_main.jsp?owncode=&stockname=&isincode=&market=1&issuetype=N&industry_code=&Page=1&chklike=Y']

        lst = []
        for url in urls:
            response = requests.get(url, headers={
                "Content-Type": "application/json",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36"
            })

            df = pd.read_html(response.text)[0][[2, 3, 5, 6]].iloc[1:]
            df.columns = ["c", "name", "type1", "type2"]
            lst.append(df)

        lst[0]["type"] = lst[0]["type2"]
        lst[1]["type"] = lst[1]["type1"]
        lst[2]["type"] = lst[2]["type1"]
        lst[3]["type"] = lst[3]["type2"]
        lst[4]["type"] = lst[4]["type1"]
        lst[5]["type"] = lst[5]["type1"]
        lst[3].loc[lst[3]["c"] == "1101B", "type"] = "水泥工業"
        lst[3].loc[lst[3]["c"] == "3036A", "type"] = "電子通路業"

        stock_list = pd.concat(lst).sort_values(
            by="c", ignore_index=True).drop(columns=["type1", "type2"])
        stock_list = stock_list.to_dict('records')
        # ================== Start to sql ==============================
        for stock in stock_list:
            StockName.objects.update_or_create(stock=stock["c"], defaults={
                'stock': stock["c"], "stockName": stock["name"], 'industry': stock["type"]})
