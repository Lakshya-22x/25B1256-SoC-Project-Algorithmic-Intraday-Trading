import pandas as pd
import numpy as np    

data = pd.read_csv("nifty.csv")[["Date","Open"]]
data["Date"] = pd.to_datetime(data["Date"], dayfirst = True)
data = data.sort_values("Date").reset_index(drop=True)
data["Open"] = data["Open"].str.replace(",","").astype(float)

data["ema20"] = np.nan
data["ema50"] = np.nan
data["ema12"] = np.nan
data["ema26"] = np.nan
data["rsi14"] = np.nan
data["macd"] = np.nan
data["signal"] = np.nan

for i in range(len(data)):
    day = i+1
    #For ema20
    a20 = 2/(20+1)
    if(day<20):
        data.loc[i,"ema20"] = np.nan
    elif(day==20):
        data.loc[i,"ema20"] = data["Open"].iloc[:day].mean()
    else:
        data.loc[i,"ema20"] = a20*data.loc[i,"Open"] + (1-a20)*data.loc[i-1,"ema20"]
    
    #For ema50
    a50 = 2/(50+1)
    if(day<50):
        data.loc[i,"ema50"] = np.nan
    elif(day==50):
        data.loc[i,"ema50"] = data["Open"].iloc[:day].mean()
    else:
        data.loc[i,"ema50"] = a50*data.loc[i,"Open"] + (1-a50)*data.loc[i-1,"ema50"]

    #ema12
    a12 = 2/(12+1)
    if(day<12):
        data.loc[i,"ema12"] = np.nan
    elif(day==12):
        data.loc[i,"ema12"] = data["Open"].iloc[:day].mean()
    else:
        data.loc[i,"ema12"] = a12*data.loc[i,"Open"] + (1-a12)*data.loc[i-1,"ema12"]
    
    #ema26
    a26 = 2/(26+1)
    if(day<26):
        data.loc[i,"ema26"] = np.nan
    elif(day==26):
        data.loc[i,"ema26"] = data["Open"].iloc[:day].mean()
    else:
        data.loc[i,"ema26"] = a26*data.loc[i,"Open"] + (1-a26)*data.loc[i-1,"ema26"]

    #macd
    if(day<26):
        data.loc[i,"macd"] = np.nan
    else:
        data.loc[i,"macd"] = data.loc[i,"ema12"] - data.loc[i,"ema26"]
    
    #macdsignal
    a9 = 2/(9+1)
    if(day<34):
        data.loc[i,"signal"] = np.nan
    elif(day==34):
        data.loc[i,"signal"] = data["macd"].iloc[25:day].mean()
    else:
        data.loc[i,"signal"] = a9*data.loc[i,"macd"] + (1-a9)*data.loc[i-1,"signal"]


#For rsi14
gain = []
loss = []
gainavg = []
lossavg = []

for i in range(len(data)):
    if(i==0):
        continue
    day = i+1
    cgain = 0
    closs = 0
    change = data.loc[i,"Open"] - data.loc[i-1,"Open"] 
    if(change>0):
        cgain = change
    else:
        closs = abs(change)
    if(day<15):
        data.loc[i,"rsi14"] = np.nan
        gain.append(cgain)
        loss.append(closs)
    elif(day==15):
        gain.append(cgain)
        loss.append(closs)
        newgainavg = np.mean(gain)
        newlossavg = np.mean(loss)
        if(newlossavg==0):
            data.loc[i,"rsi14"] = 100
        else:
            rs = (newgainavg/newlossavg)
            data.loc[i,"rsi14"] = 100 - (100/(1+rs))
        gainavg.append(newgainavg)
        lossavg.append(newlossavg)
    else:
        pgainavg = gainavg[-1]
        plossavg = lossavg[-1]  
        newgainavg = (13*pgainavg + cgain)/14
        newlossavg = (13*plossavg + closs)/14
        if(newlossavg==0):
            data.loc[i,"rsi14"] = 100
        else:
            rs = newgainavg/newlossavg
            data.loc[i,"rsi14"] = 100 - (100/(1+rs))
        gainavg.append(newgainavg)
        lossavg.append(newlossavg)

#Checking conditions
data["result"] = 0
holding = False 
for i in range(50,len(data)):
    if(not holding):
        if(data.loc[i,"ema20"]>data.loc[i,"ema50"] and data.loc[i,"rsi14"]>60 and data.loc[i,"macd"]>data.loc[i,"signal"]):
            data.loc[i,"result"] = 1
            holding = True
        else:
            data.loc[i,"result"] = 0
    elif(holding):
        if(data.loc[i,"ema20"]<data.loc[i,"ema50"] or data.loc[i,"rsi14"]<40 or data.loc[i,"macd"]<data.loc[i,"signal"]):
            data.loc[i,"result"] = -1
            holding = False
        else:
            data.loc[i,"result"] = 0

data[["Date","result"]].to_csv("final.csv", index = False)
            