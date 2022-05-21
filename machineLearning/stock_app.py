# -*- coding: utf-8 -*-
"""
@author: Zentropy
"""

import stock_feature as s
import pandas as pd
import numpy as np
import joblib


def main(stock):
    total = pd.read_csv("/app/machineLearning/total.csv")
    idx = total[total["stock"] == stock].iloc[0, -1]
    if idx == 2:
        return "ETN is unpredictable"
    model = joblib.load(f"/app/machineLearning/model_{idx}.pkl")

    df = s.data(stock)
    if df.shape[0] == 0:
        return f"stock {stock} is unpredictable"
    X = np.array(df.iloc[-1, 4:-1]).reshape(1, -1)
    y = model.predict(X)[0]

    return y


stock = str(input("股票代號："))
result = main(stock)
