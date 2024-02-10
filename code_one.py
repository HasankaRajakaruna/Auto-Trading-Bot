import pandas as pd


class CodeOne:

    def getIntervalData(self,fr):
        frame = pd.DataFrame(fr)
        frame = frame.iloc[:,:5]
        frame.columns = ['Time','Open','High','Low','Close']
        frame = frame.set_index('Time') 
        frame.index = pd.to_datetime(frame.index,unit='ms')
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
        return frame