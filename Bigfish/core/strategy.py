# -*- coding: utf-8 -*-
"""
Created on Thu Nov 26 23:25:06 2015

@author: BurdenBear
"""

class Strategy(object):
    """策略模板（可作为抽象类通过继承来使用）"""

    #----------------------------------------------------------------------
    def __init__(self, name, symbol, engine):
        """Constructor"""
        self.name = name            # 策略名称（注意唯一性）
        self.symbols = symbols        # 策略交易的合约
        self.engine = engine        # 策略引擎对象
        
        self.trading = False        # 策略是否启动交易
        
    #----------------------------------------------------------------------
    def onTick(self, tick):
        """行情更新"""
        raise NotImplementedError
    
    #----------------------------------------------------------------------
    def onTrade(self, trade):
        """交易更新"""
        raise NotImplementedError
        
    #----------------------------------------------------------------------
    def onOrder(self, order):
        """报单更新"""
        raise NotImplementedError
    
    #----------------------------------------------------------------------
    def onStopOrder(self, orderRef):
        """停止单更新"""
        raise NotImplementedError
    
    #----------------------------------------------------------------------
    def onBar(self, kbar):
        """K线数据更新"""
                
        raise NotImplementedError
        
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
        raise NotImplementedError
        
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