# -*- coding: utf-8 -*-
"""
Created on Wed Nov 25 20:46:00 2015

@author: BurdenBear
"""

import json
from Bigfish.utils.record import YieldRecord
from Bigfish.utils.common import Currency


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