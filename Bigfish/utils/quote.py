# -*- coding: utf-8 -*-
"""
Created on Thu Nov 26 10:06:21 2015

@author: BurdenBear
"""

########################################################################
class Bar:
    """K线数据对象（开高低收成交量时间）"""
    __slots__ = ["symbol", "openPrice", "highPrice", "lowPrice", "closePrice", "volume", "ctime","time_frame"]   
    def __init__(self,symbol):
        self.symbol = symbol
        self.openPrice = 0
        self.highPrice = 0
        self.lowPrice = 0
        self.closePrice = 0
        self.volume = 0
        self.ctime = 0
        self.time_frame = 0

########################################################################

class Tick:
    """Tick数据对象"""
    __DEPTH = 5    
    __slots__ = ["symbol", "openPrice", "highPrice" , "lowPrice", "lastPrice", "volume", "openInterest",
                 "upperLimit", "lowerLimit", "ctime", "ms" ]    
    __slots__.extend(["bidPrice%s"%(x+1) for x in range(__DEPTH)])
    __slots__.extend(["bidVolume%s"%(x+1) for x in range(__DEPTH)])
    __slots__.extend(["askPrice%s"%(x+1) for x in range(__DEPTH)])
    __slots__.extend(["askVolume%s"%(x+1) for x in range(__DEPTH)])
    
    @classmethod
    def get_depth(cls):
        return(cls.__DEPTH)
        
    def __init__(self, symbol):
        """Constructor"""
        self.symbol = symbol        # 合约代码
        
        self.openPrice = 0          # OHLC
        self.highPrice = 0
        self.lowPrice = 0
        self.lastPrice = 0
        
        self.volume = 0             # 成交量
        self.openInterest = 0       # 持仓量
        
        self.upperLimit = 0         # 涨停价
        self.lowerLimit = 0         # 跌停价
        
        self.ctime = 0              # 更新时间和毫秒
        self.ms= 0
        
        # 深度行情
        #TODO 用反射比正常访问慢一倍，以后再设法优化吧
        for depth in range(self.__class__.__DEPTH):
            setattr(self, "bidPrice%s"%(depth+1), 0)
            setattr(self, "bidVolume%s"%(depth+1), 0)
            setattr(self, "askPrice%s"%(depth+1), 0)
            setattr(self, "askVolume%s"%(depth+1), 0)