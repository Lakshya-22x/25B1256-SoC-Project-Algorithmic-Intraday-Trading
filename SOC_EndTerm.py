import pandas as pd
import numpy as np
import yfinance as yf
import matplotlib.pyplot as plt
 
raw = yf.download("^CRSLDX", start="2015-01-01", end="2024-01-01", progress=False)
data = pd.DataFrame()
data["Date"] = raw.index
data["Close"] = raw["Close"].values
data = data.sort_values("Date").reset_index(drop=True)
 
data["sma20"] = np.nan
data["sma50"] = np.nan
data["std20"] = np.nan
data["zscore"] = np.nan
data["momentum"] = np.nan
data["position"] = 0
data["result"] = 0
 
window = 20
window50 = 50
for i in range(len(data)):
    day = i + 1
    if day >= window:
        pricewindow = data["Close"].iloc[i - window + 1:i + 1]
        mean20 = pricewindow.mean()
        std20 = pricewindow.std()
        data.loc[i, "sma20"] = mean20
        data.loc[i, "std20"] = std20
        if std20 == 0:
            data.loc[i, "zscore"] = 0
        else:
            data.loc[i, "zscore"] = (data.loc[i, "Close"] - mean20) / std20
 
    if day >= window50:
        pricewindow50 = data["Close"].iloc[i - window50 + 1:i + 1]
        data.loc[i, "sma50"] = pricewindow50.mean()
 
lookback = 10
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
        longtrend = data.loc[i, "Close"] > data.loc[i, "sma50"]
        longmomentum = data.loc[i, "momentum"] > 0
        longnotstretched = data.loc[i, "zscore"] < 2
 
        shorttrend = data.loc[i, "Close"] < data.loc[i, "sma50"]
        shortmomentum = data.loc[i, "momentum"] < 0
        shortnotstretched = data.loc[i, "zscore"] > -2
 
        if longtrend and longmomentum and longnotstretched:
            position = 1
            entryprice = data.loc[i, "Close"]
            data.loc[i, "result"] = 1
        elif shorttrend and shortmomentum and shortnotstretched:
            position = -1
            entryprice = data.loc[i, "Close"]
            data.loc[i, "result"] = -1
        else:
            data.loc[i, "result"] = 0
 
    elif position == 1:
        stoplossprice = entryprice * (1 - stoploss_pct)
        stoplosshit = data.loc[i, "Close"] <= stoplossprice
        trendreversal = data.loc[i, "Close"] < data.loc[i, "sma50"]
        momentumreversal = data.loc[i, "momentum"] < 0
 
        if stoplosshit or (trendreversal and momentumreversal):
            data.loc[i, "result"] = -1
            position = 0
            entryprice = 0
        else:
            data.loc[i, "result"] = 0
 
    elif position == -1:
        stoplossprice = entryprice * (1 + stoploss_pct)
        stoplosshit = data.loc[i, "Close"] >= stoplossprice
        trendreversal = data.loc[i, "Close"] > data.loc[i, "sma50"]
        momentumreversal = data.loc[i, "momentum"] > 0
 
        if stoplosshit or (trendreversal and momentumreversal):
            data.loc[i, "result"] = 1
            position = 0
            entryprice = 0
        else:
            data.loc[i, "result"] = 0
 
    data.loc[i, "position"] = position
 
data[["Date", "position", "result"]].to_csv("final_endterm.csv", index=False)
 
startcapital = 100
data["wealth"] = np.nan
data.loc[0, "wealth"] = startcapital
data["benchmark"] = np.nan
data.loc[0, "benchmark"] = startcapital
 
for i in range(1, len(data)):
    prevposition = data.loc[i - 1, "position"]
    prevclose = data.loc[i - 1, "Close"]
    todayclose = data.loc[i, "Close"]
 
    if prevposition == 1:
        dailyreturn = (todayclose - prevclose) / prevclose
    elif prevposition == -1:
        dailyreturn = (prevclose - todayclose) / prevclose
    else:
        dailyreturn = 0
 
    data.loc[i, "wealth"] = data.loc[i - 1, "wealth"] * (1 + dailyreturn)
 
    benchmarkreturn = (todayclose - prevclose) / prevclose
    data.loc[i, "benchmark"] = data.loc[i - 1, "benchmark"] * (1 + benchmarkreturn)
 
years = (data.loc[len(data) - 1, "Date"] - data.loc[0, "Date"]).days / 365.25
cagr_strategy = (data.loc[len(data) - 1, "wealth"] / data.loc[0, "wealth"]) ** (1 / years) - 1
cagr_benchmark = (data.loc[len(data) - 1, "benchmark"] / data.loc[0, "benchmark"]) ** (1 / years) - 1
 
peak_strategy = data.loc[0, "wealth"]
maxdrawdown_strategy = 0
peak_benchmark = data.loc[0, "benchmark"]
maxdrawdown_benchmark = 0
 
for i in range(len(data)):
    if data.loc[i, "wealth"] > peak_strategy:
        peak_strategy = data.loc[i, "wealth"]
    drawdown_strategy = (peak_strategy - data.loc[i, "wealth"]) / peak_strategy
    if drawdown_strategy > maxdrawdown_strategy:
        maxdrawdown_strategy = drawdown_strategy
 
    if data.loc[i, "benchmark"] > peak_benchmark:
        peak_benchmark = data.loc[i, "benchmark"]
    drawdown_benchmark = (peak_benchmark - data.loc[i, "benchmark"]) / peak_benchmark
    if drawdown_benchmark > maxdrawdown_benchmark:
        maxdrawdown_benchmark = drawdown_benchmark
 
print("Strategy CAGR (%):", cagr_strategy * 100)
print("Buy and Hold CAGR (%):", cagr_benchmark * 100)
print("Strategy Max Drawdown (%):", maxdrawdown_strategy * 100)
print("Buy and Hold Max Drawdown (%):", maxdrawdown_benchmark * 100)
 
plt.figure(figsize=(12, 6))
plt.plot(data["Date"], data["wealth"], color="blue", label="Strategy")
plt.plot(data["Date"], data["benchmark"], color="orange", label="Buy and Hold")
plt.xlabel("Date")
plt.ylabel("Wealth")
plt.title("Wealth Growth Over Time")
plt.legend()
plt.grid(True)
plt.show()