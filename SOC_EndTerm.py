import pandas as pd
import numpy as np
import yfinance as yf
 
raw = yf.download("^CRSLDX", start="2015-01-01", end="2024-01-01", progress=False)
data = pd.DataFrame()
data["Date"] = raw.index
data["Close"] = raw["Close"].values
data = data.sort_values("Date").reset_index(drop=True)
 
data["sma20"] = np.nan
data["sma50"] = np.nan
data["std20"] = np.nan
data["upperband"] = np.nan
data["lowerband"] = np.nan
data["zscore"] = np.nan
data["momentum"] = np.nan
data["position"] = 0
data["result"] = 0
 
window = 20
window50 = 50
for i in range(len(data)):
    day = i + 1
    if day < window:
        continue
    else:
        pricewindow = data["Close"].iloc[i - window + 1:i + 1]
        mean20 = pricewindow.mean()
        std20 = pricewindow.std()
 
        data.loc[i, "sma20"] = mean20
        data.loc[i, "std20"] = std20
        data.loc[i, "upperband"] = mean20 + 2 * std20
        data.loc[i, "lowerband"] = mean20 - 2 * std20
 
        if std20 == 0:
            data.loc[i, "zscore"] = 0
        else:
            data.loc[i, "zscore"] = (data.loc[i, "Close"] - mean20) / std20
 
    if day >= window50:
        pricewindow50 = data["Close"].iloc[i - window50 + 1:i + 1]
        data.loc[i, "sma50"] = pricewindow50.mean()
 
lookback = 20
for i in range(len(data)):
    day = i + 1
    if day < lookback + 1:
        continue
    else:
        prevclose = data.loc[i - lookback, "Close"]
        if prevclose == 0:
            data.loc[i, "momentum"] = 0
        else:
            data.loc[i, "momentum"] = ((data.loc[i, "Close"] - prevclose) / prevclose) * 100
 
 
position = 0
entryprice = 0
stoploss_pct = 0.07
 
for i in range(window50, len(data)):
 
    if position == 0:
        longbreakout = data.loc[i, "Close"] > data.loc[i, "upperband"]
        longzscore = data.loc[i, "zscore"] > 1.5
        longmomentum = data.loc[i, "momentum"] > 0
        longtrend = data.loc[i, "Close"] > data.loc[i, "sma50"]
 
        shortbreakout = data.loc[i, "Close"] < data.loc[i, "lowerband"]
        shortzscore = data.loc[i, "zscore"] < -1.5
        shortmomentum = data.loc[i, "momentum"] < 0
        shorttrend = data.loc[i, "Close"] < data.loc[i, "sma50"]
 
        if longbreakout and longzscore and longmomentum and longtrend:
            position = 1
            entryprice = data.loc[i, "Close"]
            data.loc[i, "result"] = 1
        elif shortbreakout and shortzscore and shortmomentum and shorttrend:
            position = -1
            entryprice = data.loc[i, "Close"]
            data.loc[i, "result"] = -1
        else:
            data.loc[i, "result"] = 0
 
    elif position == 1:
        stoplossprice = entryprice * (1 - stoploss_pct)
        stoplosshit = data.loc[i, "Close"] <= stoplossprice
        trendreversal = data.loc[i, "Close"] < data.loc[i, "sma20"]
        momentumfading = data.loc[i, "momentum"] < 0
 
        if stoplosshit or (trendreversal and momentumfading):
            data.loc[i, "result"] = -1
            position = 0
            entryprice = 0
        else:
            data.loc[i, "result"] = 0
 
    elif position == -1:
        stoplossprice = entryprice * (1 + stoploss_pct)
        stoplosshit = data.loc[i, "Close"] >= stoplossprice
        trendreversal = data.loc[i, "Close"] > data.loc[i, "sma20"]
        momentumfading = data.loc[i, "momentum"] > 0
 
        if stoplosshit or (trendreversal and momentumfading):
            data.loc[i, "result"] = 1
            position = 0
            entryprice = 0
        else:
            data.loc[i, "result"] = 0
 
    data.loc[i, "position"] = position
 
data[["Date", "position", "result"]].to_csv("final_endterm.csv", index=False)