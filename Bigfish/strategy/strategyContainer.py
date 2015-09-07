# -*- coding: utf-8 -*-

from strategyEngine import *
#from utils import Series, CopyCalMethodFrom

#%%策略容器，在初始化时定制一策略代码并在Onbar函数中运行他们
########################################################################
class StrategyContainer (StrategyTemplate):
    
    #----------------------------------------------------------------------
    def __init__(self, name = 'StrategyContainer',symbol, engine):
        """Constructor"""
        self.name = name
        self.symbol = symbol        # 策略交易的合约
        self.engine = engine        # 策略引擎对象
        self.trading = False        # 策略是否启动交易
        self.strategysList = {}      # 策略字典
        
        #K线数据缓存列表
        self.listOpen = []
        self.listHigh = []
        self.listLow = []
        self.listClose = []
        self.listVolumn = []
        self.listTime = []
        #基本数据变量,账户相关变量
        self.currentbar = 0
        self.marketpositon = 0
        
        
        #在字典中保存Open,High,Low,Close,Volumn，CurrentBar，MarketPosition，
        #手动为exec语句提供local命名空间
        self.loc = {'Open':self.listOpen, \
                    'High':self.listHigh, \
                    'Low':self.listLow, \
                    'Close':self.listClose, \
                    'Volume':self.listVolume, \                    
                    'Time':self.listTime, \
                    'currentbar'= self.currentbar, \
                    'marketpositon'=self.marketpositon \
                    'sell':self.sell, \
                    'short':self.short, \
                    'buy':self.buy, \
                    'cover':self.cover}
        #在这里或者在Setting中还需添加额外的字典管理方法
        #为策略容器中所用的策略（序列和非序列）创建相应缓存变量并将名字加入字典
                    
    #----------------------------------------------------------------------
    def onBar(self, bar):
        """K线数据更新"""
        self.listOpen.append(bar.open)
        self.listHigh.append(bar.high)
        self.listLow.append(bar.low)
        self.listClose.append(bar.close)
        self.listVolume.append(bar.Volume)        
        self.listTime.append(bar.time)
        
        glb = {}
        for strategy in strategysList:
            execfile()
                
                
        
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
    def cover(self, price, volume, StopOrder=False):
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
    
        