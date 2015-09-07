# -*- coding: utf-8 -*-

from WindPy import *
from datetime import *
import time

def connectWind():
    if not w.isconnected():
        w.start()
    return w.isconnected()

def getBarData(symbol,startTime,endTime):
    if not w.isconnected():
        return None
    temp=w.wsi(symbol, ['open','high','low','close','volume'], \
    startTime.__str__(), endTime.__str__(), "")
    print(temp)
    print(temp.ErrorCode)    
    if temp.ErrorCode:
        return None    
    data=dict(zip(temp.Fields,temp.Data))
    if not 'time' in data:
        data['time'] = temp.Times
    data ['InstrumentID'] = symbol
    return data

if __name__ == '__main__':
    symbol = '000002.SZ'
    startTime = datetime(2015,8,15,9,00,00)
    endTime = datetime.fromtimestamp(int(time.time()))
    print(connectWind())    
    data = getBarData(symbol,startTime,endTime)
    print (data)