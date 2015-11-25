# -*- coding: utf-8 -*-
"""
Created on Wed Nov 25 20:46:00 2015

@author: BurdenBear
"""

import json

###################################################################
class dictlike():
    def to_dict(self):
        return ({slot:getattr(self,slot) for slot in self.__slots__})
        
###################################################################
class TranscationRecord():
    """交易记录对象"""    
    __slots__ = ["strategy", "lot", "profit", "symbol", "ctime"]
    def __init__(self, strategy="" , lot=0, profit=0, symbol="", ctime=None):
        super().__init__        
        self.strategy = strategy
        self.lot = lot
        self.profit = profit
        self.symbol = symbol
        self.ctime = ctime
        
###################################################################        
class YieldRecord(dictlike):
    """收益记录对象"""    
    __slots__ = ["yield_", "ctime"]    
    def __init__(self, yield_=0, ctime=None):
        super().__init__        
        self.yield_ = yield_
        self.ctime = ctime
     
###################################################################
class Currency:
    """货币对象"""
    def __init__(self, name=""):
        self.__name = name
        
###################################################################
class AccountManager:
    """交易账户对象"""
    
    def __init__(self, capital_base=0, name="", currency=Currency("USD")):
        self.__capital_base = capital_base
        self.__name = name
        self.__currency = currency
        self.initialize
    
    def initialize(self):
        self.__capital_net = self.__capital_base
        self.__transcation_records = []
        self.__yield_records = []
    
    def set_captital_base(self, captital_base):
        self.__captal_base = captital_base
        self.initialize
        
    def insert_record(self, record):
        """处理新增的交易记录""" 
        self.__capital_net += record.profit
        self.__transcation_records.append(record)
        self.__yield_records.append(YieldRecord(yield_=self.__capital_net/self.__captal_base*100, ctime=record.ctime))
        
    def get_records_to_json(self):
        return (json.dumps([record.to_dict() for record in self.__yield_records]))