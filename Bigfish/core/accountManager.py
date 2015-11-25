# -*- coding: utf-8 -*-
"""
Created on Wed Nov 25 20:46:00 2015

@author: BurdenBear
"""

###################################################################
class TranscationRecord:
    """交易记录对象"""    
    __slots__ = ["strategy", "lot", "profit", "symbol", "ctime"]
    def __init__(self, strategy="" , lot=0, profit=0, symbol="", ctime=None):
        self.strategy = strategy
        self.lot = lot
        self.profit = profit
        self.symbol = symbol
        self.time = time
        
###################################################################        
class YieldRecord:
    """收益记录对象"""    
    __slots__ = ["yield_", "ctime"]    
    def __init__(self, yield_=0, ctime=None):
        self.yield_ = yield_
        self.ctime = None
        
###################################################################
class Currency:
    """货币对象"""
    
    def __init__(self, name=""):
        self.__name = name
        
###################################################################
class AccountManager:
    """交易账户对象"""
    
    def __init__(capital_base=0, name="", currency=Currency("USD")):
        self.__capital_base = capital_base
        self.__name = name
        self.__currency = currency
        self.__transcation_records = []
        self.__yield_records = []
        self.initialize
    
    def initialize():
        self.__capital_net = self.__capital_base
        self.__yield_ = 0
    
    def insert_record()
    def get_profit_rep    