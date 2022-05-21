# -*- coding: utf-8 -*-
"""
@author: Zentropy
"""

def original(stock, start="2016-01-01", end="2022-12-31"):
    import yfinance as yf
    
    df = yf.download(stock+".TW", start, end, progress=False)    
    del df["Adj Close"]      
        
    return df


def feature(df):
    import talib
    
    df["adx"] = talib.ADX(df["High"], df["Low"], df["Close"], timeperiod=14) #9
    df["adxr"] = talib.ADXR(df["High"], df["Low"], df["Close"], timeperiod=14) #5
    df["dx"] = talib.DX(df["High"], df["Low"], df["Close"], timeperiod=14) #15
    df["mfi"] = talib.MFI(df["High"], df["Low"], df["Close"], df["Volume"], timeperiod=14) #14
    df["minus_di"] = talib.MINUS_DI(df["High"], df["Low"], df["Close"], timeperiod=14) #12
    df["plus_di"] = talib.PLUS_DI(df["High"], df["Low"], df["Close"], timeperiod=14) #13
    df["trix"] = talib.TRIX(df["Close"], timeperiod=30) #3
    df["ultosc"] = talib.ULTOSC(df["High"], df["Low"], df["Close"]) #16
    df["ad"] = talib.AD(df["High"], df["Low"], df["Close"], df["Volume"]) #2
    df["adosc"] = talib.ADOSC(df["High"], df["Low"], df["Close"], df["Volume"]) #8
    df["obv"] = talib.OBV(df["Close"], df["Volume"]) #1
    df["ht_dcperiod"] = talib.HT_DCPERIOD(df["Close"]) #4
    df["natr"] = talib.NATR(df["High"], df["Low"], df["Close"], timeperiod=14) #7
    df["beta"] = talib.BETA(df["High"], df["Low"], timeperiod=5) #11
    df["correl"] = talib.CORREL(df["High"], df["Low"], timeperiod=30) #6
    

def label(df): 
    def triple_barrier(price=df["Close"], ub=1.07, lb=0.97, max_period=20):
        import pandas as pd
        import numpy as np
        
        def end_price(s):
            return np.append(s[(s / s[0] > ub) | (s / s[0] < lb)], s[-1])[0]/s[0]
        
        def end_time(s):
            return np.append(r[(s / s[0] > ub) | (s / s[0] < lb)], max_period-1)[0]
    
        r = np.array(range(max_period))
        p = price.rolling(max_period).apply(end_price, raw=True).shift(-max_period+1)        

        signal = pd.Series(0, p.index)
        signal.loc[p > ub] = 1
        signal.loc[p < lb] = -1

        return signal
    
    df["y"] = triple_barrier()


def data(stock, start="2016-01-01", end="2022-12-31"):
    df = original(stock, start, end)
    if df.shape[0] == 0:
        return df
    
    feature(df)
    label(df)
    
    df.dropna(inplace=True)
    
    return df