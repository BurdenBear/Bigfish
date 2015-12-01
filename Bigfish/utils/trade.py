# -*- coding: utf-8 -*-
"""
Created on Fri Nov 27 09:59:13 2015

@author: BurdenBear
"""

class HasID:
    """有自增长ID对象的通用方法"""
    __AUTO_INC_NEXT = 0
    @classmethod 
    def next_auto_inc(cls):
        cls.__AUTO_INC_NEXT += 1
        return cls.__AUTO_INC_NEXT
    @classmethod
    def get_auto_inc(cls):
        return(cls.__AUTO_INC_NEXT)
    @classmethod
    def set_auto_inc(cls, num):
        cls.__AUTO_INC_NEXT = num 

#ENUM_POSITION_TYPE
POSITION_TYPE_BUY = 1
POSITION_TYPE_SELL = -1

class Position(HasID):
    """仓位对象"""
    
    __slots__ = ["symbol", "id", "time_open", "time_open_msc", "time_update", "time_update_msc",
                 "type_", "volume", "price_open", "price_current", "price_profit", "strategy" ]

    def __init__(self, symbol=None, prev_id=None, next_id=None):
        self.symbol = symbol
        self.id = self.__class__.next_auto_inc()
        self.prev_id = prev_id
        self.next_id = next_id
        self.time_open = None
        self.time_open_msc = None
        self.time_update = None
        self.time_update_msc = None
        self.type_ = None
        self.volume = None
        self.price_open = None
        self.price_current = None
        self.price_profit = None
        self.strategy = 0

#ENUM_ORDER_STATE
ORDER_STATE_STARTED = 0 # Order checked, but not yet accepted by broker
ORDER_STATE_PLACED = 1 # Order accepted
ORDER_STATE_CANCELED = 2 # Order canceled by client
ORDER_STATE_PARTIAL = 3 # Order partially executed
ORDER_STATE_FILLED = 4 # Order fully executed
ORDER_STATE_REJECTED = 5 # Order rejected
ORDER_STATE_EXPIRED = 6 # Order expired
ORDER_STATE_REQUEST_ADD = 7 # Order is being registered (placing to the trading system)
ORDER_STATE_REQUEST_MODIFY = 8 # Order is being modified (changing its parameters)
ORDER_STATE_REQUEST_CANCEL = 9 # Order is being deleted (deleting from the trading system)

#ENUM_ORDER_TYPE
ORDER_TYPE_BUY = 0 # Market Buy order
ORDER_TYPE_SELL = 1 # Market Sell order
ORDER_TYPE_BUY_LIMIT = 2 # Buy Limit pending order
ORDER_TYPE_SELL_LIMIT = 3 # Sell Limit pending order
ORDER_TYPE_BUY_STOP = 4 # Buy Stop pending order
ORDER_TYPE_SELL_STOP = 5 # Sell Stop pending order
ORDER_TYPE_BUY_STOP_LIMIT = 6 # Upon reaching the order price, a pending Buy Limit order is placed at the StopLimit price
ORDER_TYPE_SELL_STOP_LIMIT = 7 # Upon reaching the order price, a pending Sell Limit order is placed at the StopLimit price

#ENUM_ORDER_TYPE_FILLING
ORDER_FILLING_FOK = 0
ORDER_FILLING_IOC = 1
ORDER_FILLING_RETURN = 2

#ENUM_ORDER_TYPE_LIFE
ORDER_LIFE_GTC = 0 # Good till cancel order
ORDER_LIFE_DAY = 1 # Good till current trade day order
ORDER_LIFE_SPECIFIED = 2 # Good till expired order
ORDER_LIFE_SPECIFIED_DAY = 3 # The order will be effective till 23:59:59 of the specified day. If this time is outside a trading session, the order expires in the nearest trading time.

class Order(HasID):
    """订单对象"""
    __slots__ = ["symbol", "deal", "id", "time_setup", "time_expiration", "time_done", 
                 "time_setup_msc", "time_expiration_msc", "time_done_msc",
                 "type_", "state", "type_filling", "type_life", "volume_initial",
                 "volume_current", "price_open", "price_stop_limit", "stop_loss", 
                 "take_profit", "strategy"]
    
    def __init__(self, symbol=None, type_=None):
        self.symbol = symbol
        self.deal = None
        self.id = self.__class__.next_auto_inc()
        self.time_setup = None
        self.time_expiration = None
        self.time_done = None
        self.time_setup_msc = None
        self.time_expiration_msc = None
        self.time_done_msc = None
        self.type_ = type_
        self.state = None
        self.type_fillint = None
        self.type_life = None
        self.volume_initial = 0
        self.volume_current = 0
        self.price_open = 0
        self.price_stop_limit = 0
        self.stop_loss = 0
        self.take_profit = 0
        self.strategy = None
    
class Balance(HasID):
    """收支对象"""
    #TODO 可能并不需要
    

DEAL_ENTRY_IN = 1 # Entry in
DEAL_ENTRY_OUT = 0 # Entry out
DEAL_ENTRY_INOUT = -1 # Reverse

class Deal(HasID):
    """成交对象"""
    __slots__ = ["symbol", "id", "order", "position", "time", "time_msc", "type", 
                 "volume", "price", "commission", "profit", "strategy"]
                 
    def __init__ (self, symbol=None):
        self.symbol = symbol
        self.id = self.__class__.next_auto_inc()
        self.order = None
        self.position = None
        self.time = None
        self.time_msc = None
        self.type = None
        self.volume = 0
        self.price = 0
        self.commission = 0
        self.profit = 0
        self.strategy = 0