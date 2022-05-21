# -*- coding: utf-8 -*-
"""
@author: Zentropy
"""

import stock_feature as s
import pandas as pd
import joblib
import requests
from lightgbm import LGBMClassifier


def main():
    urls = ['https://isin.twse.com.tw/isin/class_main.jsp?owncode=&stockname=&isincode=&market=1&issuetype=1&industry_code=&Page=1&chklike=Y',
            'https://isin.twse.com.tw/isin/class_main.jsp?owncode=&stockname=&isincode=&market=1&issuetype=I&industry_code=&Page=1&chklike=Y',
            'https://isin.twse.com.tw/isin/class_main.jsp?owncode=&stockname=&isincode=&market=1&issuetype=I1&industry_code=&Page=1&chklike=Y',
            'https://isin.twse.com.tw/isin/class_main.jsp?owncode=&stockname=&isincode=&market=1&issuetype=A&industry_code=&Page=1&chklike=Y',
            'https://isin.twse.com.tw/isin/class_main.jsp?owncode=&stockname=&isincode=&market=1&issuetype=J&industry_code=&Page=1&chklike=Y',
            'https://isin.twse.com.tw/isin/class_main.jsp?owncode=&stockname=&isincode=&market=1&issuetype=N&industry_code=&Page=1&chklike=Y']

    urls_stock = []
    for url in urls:
        response = requests.get(url, headers={
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36"
        })

        df = pd.read_html(response.text)[0][[2, 3, 5, 6]].iloc[1:]
        df.columns = ["stock", "name", "type1", "type2"]
        urls_stock.append(df)

    urls_stock[0]["type"] = urls_stock[0]["type2"]
    urls_stock[1]["type"] = urls_stock[1]["type1"]
    urls_stock[2]["type"] = urls_stock[2]["type1"]
    urls_stock[3]["type"] = urls_stock[3]["type2"]
    urls_stock[4]["type"] = urls_stock[4]["type1"]
    urls_stock[5]["type"] = urls_stock[5]["type1"]
    urls_stock[3].loc[urls_stock[3]["stock"] == "1101B", "type"] = "水泥工業"
    urls_stock[3].loc[urls_stock[3]["stock"] == "3036A", "type"] = "電子通路業"

    types_stock = pd.concat(urls_stock).sort_values(
        by="stock", ignore_index=True).drop(columns=["type1", "type2"])
    types_idx = types_stock["type"].unique()
    types_stock["type_idx"] = types_stock["type"].apply(
        lambda x: (types_idx == x).argmax())
    types_stock.to_csv("/app/backend/machineLearning/total.csv", index=False)
    types_stock = pd.concat([types_stock, pd.read_csv(
        "/app/backend/machineLearning/sample.csv")]).reset_index(drop=True)

    groups = types_stock.groupby(types_stock["type_idx"])
    types = pd.read_csv("/app/backend/machineLearning/types.csv")

    for idx in types["type_idx"]:
        if idx == 2:
            continue
        stocks = groups.get_group(idx)
        types_df = pd.DataFrame()
        for stock in stocks["stock"]:
            df = s.data(stock)[:-19]
            types_df = pd.concat([types_df, df])

        params = {"n_estimators": types["n_estimators"][idx],
                  "learning_rate": types["learning_rate"][idx],
                  "max_depth": types["max_depth"][idx],
                  "num_leaves": types["num_leaves"][idx],
                  "min_data_in_leaf": types["min_data_in_leaf"][idx],
                  "lambda_l1": types["lambda_l1"][idx],
                  "lambda_l2": types["lambda_l2"][idx],
                  "min_gain_to_split": types["min_gain_to_split"][idx],
                  }

        X = types_df.iloc[:, 4:-1]
        y = types_df["y"]

        lgbc = LGBMClassifier(**params)
        lgb = lgbc.fit(X, y)

        joblib.dump(lgb, f"/app/backend/machineLearning/pkl/model_{idx}.pkl")


main()
