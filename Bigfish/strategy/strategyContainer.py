# -*- coding: utf-8 -*-
import os
import inspect
import re
from .strategyEngine import StrategyTemplate


#math包里没这个函数，自己写个
def sign (n):
    if abs(n) < 0.0000001:
        return 0
    elif n > 0:
        return 1
    elif n < 0:
        return -1
        
#%%策略容器，在初始化时定制一策略代码并在Onbar函数中运行他们
########################################################################
class StrategyContainer (StrategyTemplate):
    
    #----------------------------------------------------------------------
    def __init__(self, name, symbols, intervals, engine, code):
        """Constructor""" 
        self.name = name        
        self.intervals = intervals
        self.symbols = symbols
        self.engine = engine
        self.eventHandles = {}
        self.eventTypes = {}
        self.barDatas = {}
        
        #将策略容器与对应代码文件关联        
        self.bindCodeToStrategy(code)
        
        #基本数据变量,账户相关变量
        self.marketPosition = 0
        self.currentContracts = 0
        
        #是否完成了初始化
        self.initCompleted = False
        #在字典中保存Open,High,Low,Close,Volumn，CurrentBar，MarketPosition，
        #手动为exec语句提供local命名空间
        self.loc = {
                    'sell':self.sell, 
                    'short':self.short, 
                    'buy':self.buy, 
                    'cover':self.cover,
                    'marketposition':self.marketPosition,
                    'currentcontracts':self.currentContracts,
                    'datas':self.barDatas,
                   }
        
        #在这里或者在Setting中还需添加额外的字典管理方法
        #为策略容器中所用的策略（序列和非序列）创建相应缓存变量并将名字加入字典

    #----------------------------------------------------------------------
    def setSourcePath(self, sourcePath):
        self.sourcePath = sourcePath #设置策略代码存放目录
        
    #----------------------------------------------------------------------
    
    #将策略容器与代码文件关联
    def bindCodeToStrategy(self, code):
        
        def get_interval(interval):
            if not isinstance(interval, str):
                raise KeyError
            pattern = re.compile(r'\A(?P<period>\d{,3})(?P<freq>[md])\Z')
            match = pattern.match(interval)
            try:
                return(match.groupdict.get('period','1'),match.groupdict['freq'])
            except KeyError as e:
                print(e)
                return None
        
        loc = {}           
        exec(code,{},loc)
        for k , v in loc.items():
            if inspect.isfunction(v):
                parameters = inspect.signature(v).parameters
                intervals = parameters.get('interval',inspect._empty)
                if isinstance(intervals, str) or isinstance(intervals, tuple):
                    intervals = list[intervals]
                if intervals == inspect._empty:
                    intervals = self.intervals
                if not isinstance(intervals, list):
                    raise KeyError
                for interval in intervals:
                    period, freq = get_interval(interval)
                if freq not in self.eventTypes:                            
                    self.eventTypes[freq] = set(int(period))
                else:
                    self.eventTypes[freq].add(int(period))
                self.engine.registerEvent(EVENTS_MAP['_'.join('EVENT', freq, period)])
        print("<%s>信号添加成功" % name)
        return(True)
    
    #----------------------------------------------------------------------    
    def onTrade(self, trade):
        """交易更新"""
        """trade.direction = 1 买单,trade.direction = -1 卖单
           marketposition = 1 持多仓,-1持空仓,0为空仓
        """
        marketPosition = self.marketPosition
        if trade.direction * marketPosition >= 0:
                self.currentContracts += trade.volume
                self.marketPosition = trade.direction
        else:
                currentConstracts = self.currentContracts - trade.volume
                self.currentConstracts = abs(currentConstracts)
                self.marketPosition = marketPosition * sign(currentConstracts)
    
    #----------------------------------------------------------------------
    def onOrder(self, order):
        pass            
    
    #----------------------------------------------------------------------
    def onBar(self, bar):
        """K线数据更新"""
        self.listOpen.append(bar.open)
        self.listHigh.append(bar.high)
        self.listLow.append(bar.low)
        self.listClose.append(bar.close)
        self.listVolume.append(bar.volume)        
        self.listTime.append(bar.time)
        next(self.onBarGeneratorInstance)
                
                
        
    #----------------------------------------------------------------------
    def start(self):
        """
        启动交易
        这里是最简单的改变self.trading
        有需要可以重新实现更复杂的操作
        """
        self.trading = True
        self.engine.writeLog(self.name + u'开始运行')
        
    #----------------------------------------------------------------------
    def stop(self):
        """
        停止交易
        同上
        """
        self.trading = False
        self.engine.writeLog(self.name + u'停止运行')
        
    #----------------------------------------------------------------------
    def loadSetting(self, setting):
        """
        载入设置
        setting通常是一个包含了参数设置的字典
        """
        pass
        
    #----------------------------------------------------------------------
    def buy(self, price, volume, stopOrder=False):
        """买入开仓"""
        if self.trading:
            if stopOrder:
                so = self.engine.placeStopOrder(self.symbol, DIRECTION_BUY, 
                                                  OFFSET_OPEN, price, volume, self)
                return so
            else:
                ref = self.engine.sendOrder(self.symbol, DIRECTION_BUY,
                                              OFFSET_OPEN, price, volume, self)
                return ref
        else:
            return None
    
    #----------------------------------------------------------------------
    def cover(self, price, volume, stopOrder=False):
        """买入平仓"""
        if self.trading:
            if stopOrder:
                so = self.engine.placeStopOrder(self.symbol, DIRECTION_BUY,
                                                  OFFSET_CLOSE, price, volume, self)
                return so
            else:
                ref = self.engine.sendOrder(self.symbol, DIRECTION_BUY,
                                              OFFSET_CLOSE, price, volume, self)
                return ref
        else:
            return None
    
    #----------------------------------------------------------------------
    def sell(self, price, volume, stopOrder=False):
        """卖出平仓"""
        if self.trading:
            if stopOrder:
                so = self.engine.placeStopOrder(self.symbol, DIRECTION_SELL,
                                                  OFFSET_CLOSE, price, volume, self)
                return so
            else:
                ref = self.engine.sendOrder(self.symbol, DIRECTION_SELL,
                                              OFFSET_CLOSE, price, volume, self)
                return ref
        else:
            return None
    
    #----------------------------------------------------------------------
    def short(self, price, volume, stopOrder=False):
        """卖出开仓"""
        if self.trading:
            if stopOrder:
                so = self.engine.placeStopOrder(self.symbol, DIRECTION_SELL,
                                                  OFFSET_OPEN, price, volume, self)
                return so
            else:
                ref = self.engine.sendOrder(self.symbol, DIRECTION_SELL, 
                                              OFFSET_OPEN, price, volume, self)
                return ref    
        else:
            return None
    
    #----------------------------------------------------------------------
    def cancelOrder(self, orderRef):
        """撤单"""
        self.engine.cancelOrder(orderRef)
        
    #----------------------------------------------------------------------
    def cancelStopOrder(self, so):
        """撤销停止单"""
        self.engine.cancelStopOrder(so)
    
        