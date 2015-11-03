# -*- coding: utf-8 -*-
import os
from .strategyEngine import *


#math包里没这个函数，自己写个
def sign (n):
    if n > 0:
        return 1
    elif n < 0:
        return -1
    else:
        return 0
        
#%%策略容器，在初始化时定制一策略代码并在Onbar函数中运行他们
########################################################################
class StrategyContainer (StrategyTemplate):
    
    #----------------------------------------------------------------------
    def __init__(self, name , symbol, engine):
        """Constructor""" 
        self.name = name
        self.symbol = symbol
        self.engine = engine
        self.strategysDict = {}
        #K线数据缓存列表
        self.listOpen = []
        self.listHigh = []
        self.listLow = []
        self.listClose = []
        self.listVolume = []
        self.listTime = []
        #基本数据变量,账户相关变量
        self.marketPosition = 0
        self.currentContracts = 0
        self.onBarGeneratorInstance = self.onBarGenerator()
        #是否完成了初始化
        self.initCompleted = False
        #在字典中保存Open,High,Low,Close,Volumn，CurrentBar，MarketPosition，
        #手动为exec语句提供local命名空间
        self.loc = {'sell':self.sell, \
                    'short':self.short, \
                    'buy':self.buy, \
                    'cover':self.cover}
        #在这里或者在Setting中还需添加额外的字典管理方法
        #为策略容器中所用的策略（序列和非序列）创建相应缓存变量并将名字加入字典

    #----------------------------------------------------------------------
    def setSourcePath(self, sourcePath):
        self.sourcePath = sourcePath #设置策略代码存放目录
        
    #----------------------------------------------------------------------
    #向容器中添加策略
    def addStrategy(self, strategyName):
        filePath = self.sourcePath+'/'+strategyName+'.py'
        print(filePath)
        if not os.path.exists(filePath):
            print("信号文件不存在，请检查")            
            return(False)
        else:
            if not strategyName in self.strategysDict:
                with open(filePath, 'rb') as f:
                    code = f.read()
                    print(code)                    
                    self.strategysDict[strategyName] = compile(code,'','exec')
                    f.close()
            print(strategyName,"信号添加成功")
            return(True)
        
    #----------------------------------------------------------------------
    def onBarGenerator(self):
        if self.initCompleted == False:
            loc = self.loc
            strategysDict = self.strategysDict
            loc['Open'] = self.listOpen
            loc['High'] = self.listHigh
            loc['Low'] = self.listLow        
            loc['Close'] = self.listClose
            loc['Volume'] = self.listVolume
            loc['Time'] = self.listTime
            totalBar = 1
            glb={}
            self.initCompleted = True
        while True:
            loc['marketposition'] = self.marketPosition            
            loc['totalbar'] = totalBar
            for k , v in strategysDict.items():         
                exec(v,loc,glb)
                glb[k]()
            totalBar += 1             
            yield                    
    
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
    
        