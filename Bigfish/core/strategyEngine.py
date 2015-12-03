# -*- coding: utf-8 -*-

"""
Created on Wed Nov 25 21:09:47 2015

@author: BurdenBear
"""
import time

#自定义模块
from Bigfish.event.eventEngine.eventType import *
from Bigfish.utils.quote import Tick, Bar
from Bigfish.utils.trade import *
from Bigfish.utils.common import deque

#%% 策略引擎语句块
########################################################################
class StrategyEngine(object):
    """策略引擎"""
    CACHE_MAXLEN = 10000
    #----------------------------------------------------------------------
    def __init__(self, eventEngine, backtesting = False):
        """Constructor"""
        self.__eventEngine = eventEngine # 事件处理引擎
        self.__backtesting = backtesting # 是否为回测  
        self.__orders_done = {} # 保存所有已处理报单数据的字典
        self.__orders_todo = {} # 保存所有未处理报单（即挂单）数据的字典
        self.__deals = {} # 保存所有成交数据的字典
        self.__position = {} # 保存所有仓位信息的字典
        self.__strategys = {} # 保存策略对象的字典,key为策略名称,value为策略对象        
        self.__datas = {} # 统一的数据视图
        self.__symbols = {} # 数据中所包含的交易物品种及各自存储的长度        
        self.__map_symbol_position = {} # 保存交易物代码和有效仓位对应映射关系的字典
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
        self.__eventEngine.register(EVENT_BARDATA,self.update_bar_data)
        self.__eventEngine.register(EVENT_MARKETDATA, self.update_market_data)
        self.__eventEngine.register(EVENT_ORDER, self.update_order)
        self.__eventEngine.register(EVENT_DEAL ,self.update_deal)
        
    #----------------------------------------------------------------------
    def addStrategy(self,strategy):
        """添加已创建的策略实例"""
        self.__strategys[strategy.get_id()] = strategy
        strategy.engine = self
        self.registerStrategy(strategy.symbols, strategy)
        
    #----------------------------------------------------------------------
    def update_market_data(self, event):
        """行情更新"""       
        #TODO行情数据        
        pass
    #----------------------------------------------------------------------
    def update_bar_data(self,event):
        pass    
    #----------------------------------------------------------------------
    def __process_order(self, tick):
        """处理停止单"""
        pass

    #----------------------------------------------------------------------
    def update_order(self, event):
        """报单更新"""
        #TODO 成交更新
    #----------------------------------------------------------------------
    def update_trade(self, event):
        """成交更新"""
        #TODO 成交更新
        pass
    #----------------------------------------------------------------------
    def __update_position(self, deal):
        def sign(num):
            if abs(num) <= 10**-7:
                return(0)
            elif num > 0:
                return(1)
            else:
                return(-1)
        position_prev = self.__map_symbol_position[deal.symbol]
        position_now = Position(deal.symbol)
        position_now.prev_id = position_prev.get_id()
        position_prev.next_id = position_now.get_id()
        position = position_prev.type
        #XXX常量定义改变这里的映射函数也可能改变
        if deal.type * position >= 0:
            if position == 0:
                position_now.price_open = deal.price
                position_now.time_open = deal.time
                position_now.time_open_msc = deal.time_msc
            position_now.volume = deal.volume + position_prev.volume
            position_now.type = position
            position_now.price_current = (position_prev.price_current*position_prev.volume
            +deal.price*deal.volume)/position_now.volume 
        else:
            contracts = position_prev.volume - deal.volume
            position_now.volume = abs(constracts)
            position_now.price_current = (position_prev.price_current*position_prev.volume
            -deal.price*deal.volume)/(position_prev.volume-deal.volume)
            position_now.type = position * sign(contracts)
        position_now.time_update = deal.time
        position_now.time_update_msc = deal.time_msc
        deal.position = position_now.get_id()
        position_now.deal = deal.get_id()
        self.__map_symbol_position[deal.symbol] = position_now
    #----------------------------------------------------------------------
    def check_order(order):
        if not isinstance(Order):
            return(False)
        #TODO更多关于订单合法性的检查
        return(True)
    #----------------------------------------------------------------------
    def __send_order_to_broker(self,order):
        if self.__backtesting:
            time_now = time.time()
            order.time_done = int(time_now)
            order.time_done_msc = int((time_now-int(time_now))*(10**6))
            order.volume_current = order.volume_initial
            deal = Deal(order.symbol)
            deal.time = order.time_done
            deal.time_msc = order.time_done_msc
            deal.volume = order.volume_initial
            deal.type = 1-((order.type&1)<<1)
            deal.price = self.__datas[order.symbol]["close"][0]
            deal.profit = deal.price*deal.type*deal.volume
            #TODO加入手续费等
            order.deal = deal.get_id()
            deal.order = order.get_id()
            self.__update_position(self, deal)
            #TODO 市价单成交
        else:
            pass
            #TODO 实盘交易
    #----------------------------------------------------------------------
    def send_order(self, order):
        """
        发单（仅允许限价单）
        symbol：合约代码
        direction：方向，DIRECTION_BUY/DIRECTION_SELL
        offset：开平，OFFSET_OPEN/OFFSET_CLOSE
        price：下单价格
        volume：下单手数
        strategy：策略对象 
        """
        #TODO 更多属性的处理
        if self.check_order(order):
            time_now = time.time()
            order.time_setup = int(time_now)
            order.time_setup_msc = int((time_now-int(time_now))*(10**6))
            if order.type <= 1:#market order                        
                self.__send_order_to_broker(order)
                self.__orders_done[order.get_id()] = order 
            else:
                self.__orders_todo[order.get_id()] = order
            return(True)
        else:
            return(False)
    #----------------------------------------------------------------------
    def cancel_order(self, order_id):
        """
        撤单
        """
        if order_id == 0:
            self.__orders_todo = {}
        else:
            if order_id in self.__orders_todo:
                del(self.__orders_todo[order_id])
    #----------------------------------------------------------------------
    def register_event(self, event, handle):
        """注册事件监听"""
        #TODO  加入验证
        self.__eventEngine.register(event, handle)
    #----------------------------------------------------------------------
    def writeLog(self, log):
        """写日志"""
        event = Event(type_=EVENT_LOG)
        event.dict_['log'] = log
        self.__eventEngine.put(event)
    #----------------------------------------------------------------------
    def start_all(self):
        """启动所有策略"""
        for strategy in self.__strategys.values():
            strategy.start()         
    #----------------------------------------------------------------------
    def stop_all(self):
        """停止所有策略"""
        for strategy in self.__strategys.values():
            strategy.stop()
    #TODO 对限价单的支持    
    #----------------------------------------------------------------------
    def sell(symbol, volume, price=None, stop=False ,limit=False, strategy=None):
        order = Order(symbol, ORDER_TYPE_SELL, strategy)
        position = self.__map_symbol_position[symbol]
        if position:
            if position.type <= 0:
                return#XXX可能的返回值
        order.volume_initial = volume
        self.send_order(order)
    #----------------------------------------------------------------------
    def buy(symbol, volume, price=None, stop=False, limit=False, strategy=None):
        order = Order(symbol, ORDER_TYPE_BUY, strategy)
        position = self.__map_symbol_position[symbol]
        if position:
            if position.type < 0:
                order.volume_initial = volume + position.volume
                return(self.send_order(order))  
        order.volume_initial = volume
        return(self.send_order(order))
    #----------------------------------------------------------------------
    def cover(symbol, volume, price=None, stop=False, limit=False, strategy=None):
        order = Order(symbol, ORDER_TYPE_BUY, strategy)
        position = self.__map_symbol_position[symbol]
        if position:
            if position.type >= 0:
                return#XXX可能的返回值
        order.volume_initial = volume
        return(self.send_order(order))
    #----------------------------------------------------------------------
    def short(symbol, volume, price=None, stop=False, limit=False, strategy=None):
        order = Order(symbol, ORDER_TYPE_SELL, strategy)        
        position = self.__map_symbol_position[symbol]
        if position:
            if position.type > 0:
                order.volume_initial = volume + position.volume
                return(self.send_order(order))
        order.volume_initial = volume
        return(self.send_order(order))