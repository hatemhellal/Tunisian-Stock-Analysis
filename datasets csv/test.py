# IMPORTING PACKAGES

import pandas as pd
import matplotlib.pyplot as plt
import requests
import math
from termcolor import colored as cl
import numpy as np

plt.style.use('fivethirtyeight')
plt.rcParams['figure.figsize'] = (15, 8)

# EXTRACTING DATA



msft=pd.read_csv("servicom.csv")
msft = msft.set_index('Date Time')
msft = msft[msft.index >= '2017/01/01']
msft.index = pd.to_datetime(msft.index)
msft.to_csv('biat.csv')

# IMPORTING DATA

msft = pd.read_csv('msft.csv').set_index('Date Time')
msft.index = pd.to_datetime(msft.index)

# DEFINING SMA FUNCTION

def sma(data, n):
    sma = data.rolling(window = n).mean()
    return pd.DataFrame(sma)

n = [50, 200]
for i in n:
    msft[f'sma_{i}'] = sma(msft['Close'], i)

# PLOTTING SMA VALUES

plt.plot(msft['Close'], label = 'MSFT', linewidth = 5, alpha = 0.3)
plt.plot(msft['sma_50'], label = 'SMA 50')
plt.plot(msft['sma_200'], label = 'SMA 200')
plt.title('MSFT Simple Moving Averages (50, 200)')
plt.legend(loc = 'upper left')
plt.show()

# CREATING SMA TRADING STRATEGY

def implement_sma_strategy(data, short_window, long_window):
    sma1 = short_window
    sma2 = long_window
    buy_price = []
    sell_price = []
    sma_signal = []
    signal = 0

    for i in range(len(data)):
        if sma1[i] > sma2[i]:
            if signal != 1:
                buy_price.append(data[i])
                sell_price.append(np.nan)
                signal = 1
                sma_signal.append(signal)
            else:
                buy_price.append(np.nan)
                sell_price.append(np.nan)
                sma_signal.append(0)
        elif sma2[i] > sma1[i]:
            if signal != -1:
                buy_price.append(np.nan)
                sell_price.append(data[i])
                signal = -1
                sma_signal.append(-1)
            else:
                buy_price.append(np.nan)
                sell_price.append(np.nan)
                sma_signal.append(0)
        else:
            buy_price.append(np.nan)
            sell_price.append(np.nan)
            sma_signal.append(0)

    return buy_price, sell_price, sma_signal

sma_50 = msft['sma_50']
sma_200 = msft['sma_200']

buy_price, sell_price, signal = implement_sma_strategy(msft['Close'], sma_50, sma_200)

# PLOTTING SMA TRADE SIGNALS

plt.plot(msft['Close'], alpha = 0.3, label = 'MSFT')
plt.plot(sma_50, alpha = 0.6, label = 'SMA 50')
plt.plot(sma_200, alpha = 0.6, label = 'SMA 200')
plt.scatter(msft.index, buy_price, marker = '^', s = 200, color = 'darkblue', label = 'BUY SIGNAL')
plt.scatter(msft.index, sell_price, marker = 'v', s = 200, color = 'crimson', label = 'SELL SIGNAL')
plt.legend(loc = 'upper left')
plt.title('MSFT SMA CROSSOVER TRADING SIGNALS')
plt.show()

# OUR POSITION IN STOCK (HOLD/SOLD)

position = []
for i in range(len(signal)):
    if signal[i] > 1:
        position.append(0)
    else:
        position.append(1)

for i in range(len(msft['Close'])):
    if signal[i] == 1:
        position[i] = 1
    elif signal[i] == -1:
        position[i] = 0
    else:
        position[i] = position[i-1]

# CONSOLIDATING LISTS TO DATAFRAME

sma_20 = pd.DataFrame(sma_50).rename(columns = {0:'sma_50'})
sma_50 = pd.DataFrame(sma_200).rename(columns = {0:'sma_200'})
buy_price = pd.DataFrame(buy_price).rename(columns = {0:'buy_price'}).set_index(msft.index)
sell_price = pd.DataFrame(sell_price).rename(columns = {0:'sell_price'}).set_index(msft.index)
signal = pd.DataFrame(signal).rename(columns = {0:'sma_signal'}).set_index(msft.index)
position = pd.DataFrame(position).rename(columns = {0:'sma_position'}).set_index(msft.index)

frames = [sma_20, sma_50, buy_price, sell_price, signal, position]
strategy = pd.concat(frames, join = 'inner', axis = 1)
strategy = strategy.reset_index().drop('Date Time', axis = 1)

# BACKTESTING THE STRAGEGY

msft_ret = pd.DataFrame(np.diff(msft['Close'])).rename(columns = {0:'returns'})
sma_strategy_ret = []

for i in range(len(msft_ret)):
    try:
        returns = msft_ret['returns'][i]*strategy['sma_position'][i]
        sma_strategy_ret.append(returns)
    except:
        pass

sma_strategy_ret_df = pd.DataFrame(sma_strategy_ret).rename(columns = {0:'sma_returns'})

investment_value = 100000
number_of_stocks = math.floor(investment_value/msft['Close'][1])
sma_investment_ret = []

for i in range(len(sma_strategy_ret_df['sma_returns'])):
    returns = number_of_stocks*sma_strategy_ret_df['sma_returns'][i]
    sma_investment_ret.append(returns)

sma_investment_ret_df = pd.DataFrame(sma_investment_ret).rename(columns = {0:'investment_returns'})
total_investment_ret = round(sum(sma_investment_ret_df['investment_returns']), 2)
print(cl('Profit gained from the strategy by investing $100K in MSFT : ${} in 1 Year'.format(total_investment_ret), attrs = ['bold']))
