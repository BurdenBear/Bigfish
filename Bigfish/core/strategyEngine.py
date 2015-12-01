# -*- coding: utf-8 -*-

"""
Created on Wed Nov 25 21:09:47 2015

@author: BurdenBear
"""

#自定义模块
from Bigfish.event.eventEngine.eventType import *
from Bigfish.utils.quote import Tick, Bar
from Bigfish.utils.trade import Order, Deal, Position
from Bigfish.utils.common import deque

# 常量定义
OFFSET_OPEN = 1           # 开仓
OFFSET_CLOSE = -1          # 平仓

DIRECTION_BUY = 1         # 买入
DIRECTION_SELL = -1        # 卖出

PRICETYPE_LIMIT = 2      # 限价

#%% 数据类型定义语句块


########################################################################
class Trade:
    """成交数据对象"""

    #----------------------------------------------------------------------
    def __init__(self, symbol):
        """Constructor"""
        self.symbol = symbol        # 合约代码
        
        self.orderRef = ''          # 报单号
        self.tradeID = ''           # 成交编号
        
        self.direction = None       # 方向
        self.offset = None          # 开平
        self.price = 0              # 成交价
        self.volume = 0             # 成交量
 
########################################################################
class StopOrder:
    """
    停止单对象
    用于实现价格突破某一水平后自动追入
    即通常的条件单和止损单
    """

    #----------------------------------------------------------------------
    def __init__(self, symbol, direction, offset, price, volume, strategy):
        """Constructor"""
        self.symbol = symbol
        self.direction = direction
        self.offset = offset
        self.price = price
        self.volume = volume
        self.strategy = strategy

#%% 策略引擎语句块
########################################################################
class StrategyEngine(object):
    """策略引擎"""
    CACHE_MAXLEN = 10000
    #----------------------------------------------------------------------
    def __init__(self, eventEngine, backtesting = False):
        """Constructor"""
        self.__eventEngine = eventEngine #事件处理引擎
        self.__backtesting = backtesting # 是否为回测  
        self.__orders = {} # 保存所有报单数据的字典
        self.__deals = {} # 保存所有成交数据的字典
        self.__position = {} # 保存所有仓位信息的字典
        self.__strategys = {} # 保存策略对象的字典,key为策略名称,value为策略对象
        self.__map_symbol_strategys = {} # 保存合约代码和策略对象映射关系的字典
        self.__datas = {} # 统一的数据视图
        self.__symbols = {} # 数据中所包含的交易物品种及各自存储的长度
        self.__map_symbol_position = {}
        # 保存策略将使用到的与某标的物有关事件
        # key为标的物代码
        # value为标的物数据更新有关的事件
        self.__eventType = {}
    #----------------------------------------------------------------------
    def get_currentcontracts():
        #TODO 现在持仓手数        
        return()
    #----------------------------------------------------------------------
    def get_positions(self):
        #TODO 读取每个品种的有效Position       
        return(self.__map_symbol_position)
    #----------------------------------------------------------------------
    def get_datas(self):
        return(self.__datas)
    #----------------------------------------------------------------------
    def add_symbols(self, symbols, max_length = 0):
        for symbol in symbols:
            if symbol not in self.__symbols:
                self.__symbols[symbol] = 0
            if max_length > self.__symbols[symbol]:
                self.__symbols[symbol] = max_length
    #----------------------------------------------------------------------
    def initialize(self):
        #TODO数据结构还需修改        
        for symbol, maxlen in symbols.items():
            if maxlen == 0:
                self.__datas=deque([],maxlen=self.CACHE_MAXLEN)
            else:
                self.__datas=deque([],maxlen=maxlen)
        
    #----------------------------------------------------------------------
    def addStrategy(self,strategy):
        """添加已创建的策略实例"""
        self.__strategys[strategy.name] = strategy
        strategy.engine = self
        self.registerStrategy(strategy.symbols, strategy)
        
    #----------------------------------------------------------------------
    def createStrategy(self, strategyName, strategySymbol, strategyClass, strategySetting):
        """创建策略"""
        strategy = strategyClass(strategyName, strategySymbol, self)
        self.__strategys[strategyName] = strategy
        strategy.loadSetting(strategySetting)
        
        # 订阅合约行情，注意这里因为是CTP，所以ExchangeID可以忽略
        self.mainEngine.subscribe(strategySymbol, None)
        
        # 注册策略监听
        self.registerStrategy(strategySymbol, strategy)

    #----------------------------------------------------------------------
    def updateMarketData(self, event):
        """行情更新"""       
        tick = event.content['data']
        symbol = tick.symbol       
        # 检查是否存在交易该合约的策略
        if symbol in self.__map_symbol_strategys:
            # 首先检查停止单是否需要发出
            self.__processStopOrder(tick)
            
            # 将该TICK数据推送给每个策略
            for strategy in self.__map_symbol_strategys[symbol]:
                strategy.onTick(tick) 
        
        # 将数据插入MongoDB数据库，实盘建议另开程序记录TICK数据
        self.__recordTick(data)
        
    #----------------------------------------------------------------------
    def updateBarData(self,event):
        data = event.content['data']
        symbol = data['InstrumentID']
        
        if symbol in self.__map_symbol_strategys:
            bar = Bar(symbol)
            bar.open = data['Open']
            bar.high = data['High']
            bar.low = data['Low']
            bar.close = data['Close']
            bar.volume = data['Volume']
            bar.time = data['Time']
            
            #将K线数据推送给每个策略
            for strategy in self.__map_symbol_strategys[symbol]:
                strategy.onBar(bar)
            
            
    #----------------------------------------------------------------------
    def __processStopOrder(self, tick):
        """处理停止单"""
        symbol = tick.symbol
        lastPrice = tick.lastPrice
        upperLimit = tick.upperLimit
        lowerLimit = tick.lowerLimit
        
        # 如果当前有该合约上的止损单
        if symbol in self.__dictStopOrder:
            # 获取止损单列表
            listSO = self.__dictStopOrder[symbol]     # SO:stop order
            
            # 准备一个空的已发止损单列表
            listSent = []
            
            for so in listSO:
                # 如果是买入停止单，且最新成交价大于停止触发价
                if so.direction == DIRECTION_BUY and lastPrice >= so.price:
                    # 以当日涨停价发出限价单买入
                    ref = self.sendOrder(symbol, DIRECTION_BUY, so.offset, 
                                         upperLimit, so.volume, strategy)    
                    
                    # 触发策略的止损单发出更新
                    so.strategy.onStopOrder(ref)
                    
                    # 将该止损单对象保存到已发送列表中
                    listSent.append(so)
                
                # 如果是卖出停止单，且最新成交价小于停止触发价
                elif so.direction == DIRECTION_SELL and lastPrice <= so.price:
                    ref = self.sendOrder(symbol, DIRECTION_SELL, so.offset,
                                         lowerLimit, so.volume, strategy)
                    
                    so.strategy.onStopOrder(ref)
                    
                    listSent.append(so)
                    
            # 从停止单列表中移除已经发单的停止单对象
            if listSent:
                for so in listSent:
                    listSO.remove(so)
                    
            # 检查停止单列表是否为空，若为空，则从停止单字典中移除该合约代码
            if not listSO:
                del self.__dictStopOrder[symbol]

    #----------------------------------------------------------------------
    def updateOrder(self, event):
        """报单更新"""
        data = event.dict_['data']
        orderRef = data['OrderRef']
        
        # 检查是否存在监听该报单的策略
        if orderRef in self.__map_order_strategy:
            
            # 创建Order数据对象
            order = Order(data['InstrumentID'])
            
            order.orderRef = data['OrderRef']
            order.direction = data['Direction']
            order.offset = data['CombOffsetFlag']
            
            order.price = data['LimitPrice']
            order.volumeOriginal = data['VolumeTotalOriginal']
            order.volumeTraded = data['VolumeTraded']
            order.insertTime = data['InsertTime']
            order.cancelTime = data['CancelTime']
            order.frontID = data['FrontID']
            order.sessionID = data['SessionID']
            
            order.status = data['OrderStatus']
            
            # 推送给策略
            strategy = self.__map_order_strategy[orderRef]
            strategy.onOrder(order)
            
        # 记录该Order的数据
        self.__orders[orderRef] = data
    
    #----------------------------------------------------------------------
    def updateTrade(self, event):
        """成交更新"""
        print ('updateTrade')
        data = event.dict_['data']
        orderRef = data['OrderRef']
        print ('trade:', orderRef)
        
        if orderRef in self.__map_order_strategy:
            
            # 创建Trade数据对象
            trade = Trade(data['InstrumentID'])
            
            trade.orderRef = orderRef
            trade.tradeID = data['TradeID']
            trade.direction = data['Direction']
            trade.offset = data['OffsetFlag']
    
            trade.price = data['Price']
            trade.volume = data['Volume']
            
            # 推送给策略
            strategy = self.__map_order_strategy[orderRef]
            strategy.onTrade(trade)            
        
    #----------------------------------------------------------------------
    def sendOrder(self, symbol, direction, offset, price, volume, strategy):
        """
        发单（仅允许限价单）
        symbol：合约代码
        direction：方向，DIRECTION_BUY/DIRECTION_SELL
        offset：开平，OFFSET_OPEN/OFFSET_CLOSE
        price：下单价格
        volume：下单手数
        strategy：策略对象 
        """
        contract = self.mainEngine.selectInstrument(symbol)
        
        if contract:
            ref = self.mainEngine.sendOrder(symbol,
                                            contract['ExchangeID'],
                                            price,
                                            PRICETYPE_LIMIT,
                                            volume,
                                            direction,
                                            offset)
            
        self.__map_order_strategy[ref] = strategy
        print ('ref:', ref)
        print ('strategy:', strategy.name)
        
        return ref

    #----------------------------------------------------------------------
    def cancelOrder(self, orderRef):
        """
        撤单
        """
        order = self.__orders[orderRef]
        symbol = order['InstrumentID']
        contract = self.mainEngine.selectInstrument(symbol)
        
        if contract:
            self.mainEngine.cancelOrder(symbol,
                                        contract['ExchangeID'],
                                        orderRef,
                                        order['FrontID'],
                                        order['SessionID'])
        
    #----------------------------------------------------------------------
    def registerEvent(self, event, handle):
        """注册事件监听"""
        #TODO  加入验证
        self.__eventEngine.register(event, handle)
        """
        self.__eventEngine.register(EVENT_BARDATA,self.updateBarData)
        self.__eventEngine.register(EVENT_MARKETDATA, self.updateMarketData)
        self.__eventEngine.register(EVENT_ORDER, self.updateOrder)
        self.__eventEngine.register(EVENT_TRADE ,self.updateTrade)
        """
        
    #----------------------------------------------------------------------
    def writeLog(self, log):
        """写日志"""
        event = Event(type_=EVENT_LOG)
        event.dict_['log'] = log
        self.__eventEngine.put(event)
        
    #----------------------------------------------------------------------
    def registerStrategy(self, symbol, strategy):
        """注册策略对合约TICK数据的监听"""
        # 尝试获取监听该合约代码的策略的列表，若无则创建
        try:
            listStrategy = self.__map_symbol_strategys[symbol]
        except KeyError:
            listStrategy = []
            self.__map_symbol_strategys[symbol] = listStrategy
        
        # 防止重复注册
        if strategy not in listStrategy:
            listStrategy.append(strategy)

    #----------------------------------------------------------------------
    def placeStopOrder(self, symbol, direction, offset, price, volume, strategy):
        """
        下停止单（运行于本地引擎中）
        注意这里的price是停止单的触发价
        """
        # 创建止损单对象
        so = StopOrder(symbol, direction, offset, price, volume, strategy)
        
        # 获取该合约相关的止损单列表
        try:
            listSO = self.__dictStopOrder[symbol]
        except KeyError:
            listSO = []
            self.__dictStopOrder[symbol] = listSO
        
        # 将该止损单插入列表中
        listSO.append(so)
        
        return so
    
    #----------------------------------------------------------------------
    def cancelStopOrder(self, so):
        """撤销停止单"""
        symbol = so.symbol
        
        try:
            listSO = self.__dictStopOrder[symbol]

            if so in listSO:
                listSO.remove(so)
            
            if not listSO:
                del self.__dictStopOrder[symbol]
        except KeyError:
            pass
        
    #----------------------------------------------------------------------
    def startAll(self):
        """启动所有策略"""
        for strategy in self.__strategys.values():
            strategy.start()
            
    #----------------------------------------------------------------------
    def stopAll(self):
        """停止所有策略"""
        for strategy in self.__strategys.values():
            strategy.stop()
    
    