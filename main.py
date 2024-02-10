
import pandas as pd
import talib
import numpy as np
from binance import Client
import time

API_KEY = "api_key"
API_SECRET = "api_secret"

client = Client(API_KEY,API_SECRET)

array_high = []
array_low = []
array_close = []
array_rsi = []
array_sma = []
array_longStop = []
array_longStopPrev = []
array_shortStop = []
array_shortStopPrev = []
array_dir = []
singalValue = ""


def getIntervalDataFirst(symbol,interval,lookback):
    frame = pd.DataFrame(client.get_historical_klines(symbol,interval,lookback+' min ago UTC'))
    frame = frame.iloc[:,:5]
    frame.columns = ['Time','Open','High','Low','Close']
    frame = frame.set_index('Time') 
    # frame.index = pd.to_datetime(frame.index,unit='ms')
    frame = frame.astype(float)
    
    #Heikin ashi candles
    frame['Close'] = (frame['Open'] + frame['High'] + frame['Low'] + frame['Close']) / 4
    
    for i in range(len(frame)):
        if i == 0:
            frame.iat[0, 0] = frame['Open'].iloc[0]
        else:
            frame.iat[i, 0] = (frame.iat[i-1, 0] + frame.iat[i-1, 3]) / 2
        
    frame['High'] = frame.loc[:, ['Open', 'Close']].join(frame['High']).max(axis=1)
    frame['Low'] = frame.loc[:, ['Open', 'Close']].join(frame['Low']).min(axis=1)

    global array_high
    global array_low 
    global array_close
    array_high =  frame['High'].to_numpy()
    array_low =  frame['Low'].to_numpy()
    array_close =  frame['Close'].to_numpy()


def getIntervalDataSecond(symbol,interval,lookback):
    frame = pd.DataFrame(client.get_historical_klines(symbol,interval,lookback+' min ago UTC'))
    frame = frame.iloc[:,:5]
    frame.columns = ['Time','Open','High','Low','Close']
    frame = frame.set_index('Time') 
    # frame.index = pd.to_datetime(frame.index,unit='ms')
    frame = frame.astype(float)
    
    #Heikin ashi candles
    frame['Close'] = (frame['Open'] + frame['High'] + frame['Low'] + frame['Close']) / 4
    
    for i in range(len(frame)):
        if i == 0:
            frame.iat[0, 0] = frame['Open'].iloc[0]
        else:
            frame.iat[i, 0] = (frame.iat[i-1, 0] + frame.iat[i-1, 3]) / 2
        
    frame['High'] = frame.loc[:, ['Open', 'Close']].join(frame['High']).max(axis=1)
    frame['Low'] = frame.loc[:, ['Open', 'Close']].join(frame['Low']).min(axis=1)

    global array_high
    global array_low 
    global array_close

    array_high = np.append(array_high,frame.High[49])
    array_low = np.append(array_low,frame.Low[49])
    array_close = np.append(array_close,frame.Close[49])

    array_high = np.delete(array_high,0)
    array_low = np.delete(array_low,0)
    array_close = np.delete(array_close,0)
    

def RsiIndicator(arry_close,interval):
    global array_rsi 
    array_rsi = np.array(talib.RSI(arry_close,timeperiod=interval)) 



def SmaIndicator(arry_rsi,interval):
    global array_sma
    array_sma = np.array(talib.SMA(arry_rsi, timeperiod=interval))


def ChandelierOne(array_high,array_low,array_close,mul,length):

    #Calculating ATR value
    array_atr = np.array(talib.ATR(array_high,array_low, array_close, timeperiod=length))
    for y in range(len(array_atr)):
        array_atr[y] = array_atr[y]*mul
        
    #calculating LongStop value
    global array_longStop
    global array_longStopPrev
    array_longStop = np.zeros(len(array_close))
    array_longStopPrev = np.zeros(len(array_close))
    
    for x in range(len(array_close)):
        array_longStop[x] = array_close[x] - array_atr[x]
        if(x>0):   
            array_longStopPrev[x] = array_longStop[x-1]
            if(array_close[x-1] > array_longStopPrev[x]):
                array_longStop[x] = max(array_longStop[x], array_longStopPrev[x]) 


    #calculating ShortStop value  
    global array_shortStop
    global array_shortStopPrev
    array_shortStop = np.zeros(len(array_close))
    array_shortStopPrev = np.zeros(len(array_close))
    
    for x in range(len(array_close)):
        array_shortStop[x] = array_close[x] + array_atr[x]
        if(x>0):
            array_shortStopPrev[x] = array_shortStop[x-1]
            if(array_close[x-1] < array_shortStopPrev[x]):
                array_shortStop[x] = min(array_shortStop[x], array_shortStopPrev[x])

    #Calculating Dir value    
    global array_dir
    array_dir = np.zeros(len(array_close))
    dir = -1
    
    for z in range(len(array_close)):
        if (array_close[z] > array_shortStopPrev[z]):
            array_dir[z] = 1
            dir = 1
        elif(array_close[z] < array_longStopPrev[z]):
            array_dir[z] = -1
            dir = -1
        else:
            array_dir[z] = dir

def ChandelierTwo(array_high,array_low,array_close,mul,length):

    #Calculating ATR value
    array_atr = np.array(talib.ATR(array_high,array_low, array_close, timeperiod=length))
    for y in range(len(array_atr)):
        array_atr[y] = array_atr[y]*mul
        
    #calculating LongStop value
    global array_longStop
    global array_longStopPrev

    l_value = 149
    longStop = array_close[l_value] - array_atr[149]
    array_longStop = np.append(array_longStop,longStop)
    array_longStop = np.delete(array_longStop,0)

    array_longStopPrev = np.append(array_longStopPrev,array_longStop[l_value-1])
    array_longStopPrev = np.delete(array_longStopPrev,0)
    
    if(array_close[l_value-1] > array_longStopPrev[l_value]):
        array_longStop[l_value] = max(array_longStop[l_value], array_longStopPrev[l_value]) 


    #calculating ShortStop value  
    global array_shortStop
    global array_shortStopPrev

    shortStop = array_close[l_value] + array_atr[149]
    array_shortStop = np.append(array_shortStop,shortStop)
    array_shortStop = np.delete(array_shortStop,0)

    array_shortStopPrev = np.append(array_shortStopPrev,array_shortStop[l_value-1])
    array_shortStopPrev = np.delete(array_shortStopPrev,0)
    
    if(array_close[l_value-1] < array_shortStopPrev[l_value]):
        array_shortStop[l_value] = min(array_shortStop[l_value], array_shortStopPrev[l_value])

    #Calculating Dir value    
    global array_dir
    dir = array_dir[l_value]
    array_dir = np.delete(array_dir,0)
    if (array_close[l_value] > array_shortStopPrev[l_value]):
        array_dir = np.append(array_dir,1)
    elif(array_close[l_value] < array_longStopPrev[l_value]):
        array_dir = np.append(array_dir,-1)
    else:
        array_dir = np.append(array_dir,dir)

    global singalValue

    if(array_dir[l_value] == 1 and array_dir[l_value-1] == -1):
        singalValue = "buy"
    elif(array_dir[l_value] == -1 and array_dir[l_value-1] == 1):
        singalValue = "sell"
    else:
        singalValue = "none"

def get_seconds_to_close(symbol,interval,lookback):
    timestamp = pd.DataFrame(client.get_historical_klines(symbol,interval,lookback+' min ago UTC'))
    mseconds = 3600000
    needed_timestamp = timestamp[0]+ mseconds
    current_time = client.get_server_time()
    seconds_left = (needed_timestamp-current_time['serverTime'])/1000
    return seconds_left


def Strategy():

    l_value = 149
    
    if(singalValue=="buy" and (array_rsi[l_value] > array_sma[l_value])):
        pass

    if(singalValue=="sell" and (array_rsi[l_value] < array_sma[l_value])):
        pass

    while True:
        df = getIntervalData('BTCUSDT','5m','150')
        timer = get_seconds_to_close('BTCUSDT','1h','150')
        time.sleep(timer)

Strategy()
    
#Error
# 225 how to get hour data

    



