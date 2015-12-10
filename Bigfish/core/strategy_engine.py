# -*- coding: utf-8 -*-

"""
Created on Wed Nov 25 21:09:47 2015

@author: BurdenBear
"""
import time

#自定义模块
from Bigfish.event.event import *
from Bigfish.event.engine import EventEngine
from Bigfish.utils.trade import *
from Bigfish.utils.common import deque
from Bigfish.event.handle import SymbolsListener
from functools import partial

#%% 策略引擎语句块
########################################################################
class StrategyEngine(object):
    """策略引擎"""
    CACHE_MAXLEN = 10000
    #----------------------------------------------------------------------
    def __init__(self, event_engine=EventEngine(), backtesting = False):
        """Constructor"""
        self.__event_engine = event_engine # 事件处理引擎
        self.__backtesting = backtesting # 是否为回测  
        self.__orders_done = {} # 保存所有已处理报单数据的字典
        self.__orders_todo = {} # 保存所有未处理报单（即挂单）数据的字典
        self.__deals = {} # 保存所有成交数据的字典
        self.__position = {} # 保存所有仓位信息的字典
        self.__strategys = {} # 保存策略对象的字典,key为策略名称,value为策略对象        
        self.__datas = {} # 统一的数据视图
        self.__symbols = {} # 数据中所包含的交易物品种及各自存储的长度        
        self.start_time = None
        self.end_time = None        
        self.__map_symbol_position = {} # 保存交易物代码和有效仓位对应映射关系的字典
    #TODO单独放入utils中
    def get_attr(self, attr=''):
        return(getattr(self,'_%s__%s'%(self.__class__.__name__,attr)))
    def set_attr(self, value, attr='', check=lambda x:None, handle=None):
        after_check = check(value)
        if not after_check:
            setattr(self,'_%s__%s'%(self.__class__.__name__,attr),value)
        elif handle:
            setattr(self,'_%s__%s'%(self.__class__.__name__,attr),handle(check))
    symbols = property(partial(get_attr,attr='symbols'), None, None)
    start_time = property(partial(get_attr,attr='start_time'), partial(set_attr,attr='start_time'),None)
    end_time = property(partial(get_attr,attr='end_time'), partial(set_attr,attr='end_time'),None)
    #----------------------------------------------------------------------
    def get_currentcontracts(self):
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
    def add_symbols(self, symbols, time_frame, max_length = 0):
        for symbol in symbols:
            if (symbol,time_frame) not in self.__symbols:
                self.__symbols[(symbol,time_frame)] = max_length
            self.__symbols[(symbol,time_frame)] = max(max_length, self.__symbols[(symbol,time_frame)])
            self.register_event(EVENT_BAR_SYMBOL[symbol][time_frame],self.update_bar_data)
    #----------------------------------------------------------------------
    def initialize(self):
        #TODO数据结构还需修改
        for (symbol, time_frame), maxlen in self.__symbols.items():
            for field in ['open','high','low','close','time','volume']:
                if not symbol in self.__datas:
                    self.__datas[symbol] = {}
                if not time_frame in self.__datas[symbol]:
                    self.__datas[symbol][time_frame] = {}
                if maxlen == 0:
                    maxlen = self.CACHE_MAXLEN
                for field in ['open','high','low','close','time','volume']:
                    self.__datas[symbol][time_frame][field] = deque(maxlen=maxlen)
    #----------------------------------------------------------------------
    def add_strategy(self,strategy):
        """添加已创建的策略实例"""
        self.__strategys[strategy.get_id()] = strategy
        strategy.engine = self    
    #----------------------------------------------------------------------
    def update_market_data(self, event):
        """行情更新"""       
        #TODO行情数据        
        pass
    #----------------------------------------------------------------------
    def update_bar_data(self,event):
        bar = event.content['data']
        symbol = bar.symbol
        time_frame = bar.time_frame
        for field in ['open','high','low','close','time','volume']:
            self.__datas[symbol][time_frame][field].appendleft(getattr(bar,field))
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
            return(deal)
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
            if order.type <= 1:#market order                        
                self.__engine.async_handle(self.__send_order_to_broker(order),self.__update_position())
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
    def put_event(self, event):
        #TODO 加入验证
        self.__event_engine.put(event)
    #----------------------------------------------------------------------   
    def register_event(self, event_type, handle):
        """注册事件监听"""
        #TODO  加入验证
        self.__event_engine.register(event_type, handle)
    def unregister_event(self, event_type, handle):
        self.__event_engine.unregister(event_type, handle)
    #----------------------------------------------------------------------
    def writeLog(self, log):
        """写日志"""
        event = Event(type_=EVENT_LOG)
        event.content['log'] = log
        self.__event_engine.put(event)
    #----------------------------------------------------------------------
    def start(self):
        """启动所有策略"""
        self.__event_engine.start()
        for strategy in self.__strategys.values():
            strategy.start()         
    #----------------------------------------------------------------------
    def stop(self):
        """停止所有策略"""
        self.__event_engine.stop()        
        for strategy in self.__strategys.values():
            strategy.stop()        
    #TODO 对限价单的支持    
    #----------------------------------------------------------------------
    def sell(symbol, volume=1, price=None, stop=False ,limit=False, strategy=None, listner=None):
        if volume == 0: return        
        position = self.__map_symbol_position.get(symbol,None)
        if not position or position.type <= 0:
            return#XXX可能的返回值
        order = Order(symbol, ORDER_TYPE_SELL, strategy)
        order.volume_initial = volume
        if self.__backtesting:
            time_ = self.__datas[symbol][SymbolsListener.get_by_id(listner).get_time_frame()]['time']
        else:
            time_ = time.time()
        order.time_setup = int(time_)
        order.time_setup_msc = int((time_ - int(time_))*(10**6))
        return(self.send_order(order))
    #----------------------------------------------------------------------
    def buy(symbol, volume=1, price=None, stop=False, limit=False, strategy=None, listner=None):
        if volume == 0: return
        position = self.__map_symbol_position.get(symbol,None)        
        order = Order(symbol, ORDER_TYPE_BUY, strategy)
        if position and position.type < 0:
            order.volume_initial = volume + position.volume
        else:
            order.volume_initial = volume
        if self.__backtesting:
            time_ = self.__datas[symbol][SymbolsListener.get_by_id(listner).get_time_frame()]['time']
        else:
            time_ = time.time()
        order.time_setup = int(time_)
        order.time_setup_msc = int((time_ - int(time_))*(10**6))
        return(self.send_order(order))
    #----------------------------------------------------------------------
    def cover(symbol, volume=1, price=None, stop=False, limit=False, strategy=None, listner=None):
        if volume == 0: return        
        position = self.__map_symbol_position.get(symbol,None)        
        order = Order(symbol, ORDER_TYPE_BUY, strategy)
        if not position or position.type >= 0:
            return#XXX可能的返回值
        order.volume_initial = volume
        if self.__backtesting:
            time_ = self.__datas[symbol][SymbolsListener.get_by_id(listner).get_time_frame()]['time']
        else:
            time_ = time.time()
        order.time_setup = int(time_)
        order.time_setup_msc = int((time_ - int(time_))*(10**6))
        return(self.send_order(order))
    #----------------------------------------------------------------------
    def short(symbol, volume=1, price=None, stop=False, limit=False, strategy=None, listner=None):
        if volume == 0: return        
        position = self.__map_symbol_position.get(symbol,None)        
        order = Order(symbol, ORDER_TYPE_SELL, strategy)        
        if position and position.type > 0:
            order.volume_initial = volume + position.volume
        else:
            order.volume_initial = volume
        if self.__backtesting:
            time_ = self.__datas[symbol][SymbolsListener.get_by_id(listner).get_time_frame()]['time']
        else:
            time_ = time.time()
        order.time_setup = int(time_)
        order.time_setup_msc = int((time_ - int(time_))*(10**6))
        return(self.send_order(order))