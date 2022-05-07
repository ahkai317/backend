# ========= django setting required ===============
from django.core.management.base import BaseCommand
from sqlalchemy import create_engine
from backend import settings

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

        df = []
        for url in urls:
            response = requests.get(url, headers={
                "Content-Type": "application/json",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36"
            })

            df.append(pd.read_html(response.text)[0].iloc[1:, 2:8])

        result = pd.concat(df).sort_values(by=2).reset_index(drop=True)
        result[7] = result[7].apply(lambda x: datetime.strptime(x, "%Y/%m/%d"))
        result[6].where(result[5] != 'ETF', result[5], inplace=True)
        result[6].where(result[5] != 'ETN', result[5], inplace=True)
        result[6].where(result[5] != '受益證券-不動產投資信託', '受益證券', inplace=True)
        result[6].where(result[5] != '臺灣存託憑證(TDR)', '存託憑證', inplace=True)
        result[6].where(pd.notna(result[6]), '無分類', inplace=True)
        result.columns = ['stock', 'stockName', 'market',
                        'securities', 'industry', 'list_date']
        result['updated'] = datetime.now()

        #================== Start to sql ==============================         

        database = settings.DATABASES['default']['NAME']
        user = settings.DATABASES['default']['USER']
        password = settings.DATABASES['default']['PASSWORD']
        host = settings.DATABASES['default']['HOST']
        port = settings.DATABASES['default']['PORT']

        engine = create_engine(f"mysql://{user}:{password}@{host}:{port}/{database}?charset=utf8")

        result.to_sql(StockName._meta.db_table, con=engine, if_exists='replace',index=False)

