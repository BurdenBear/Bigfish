# -*- coding: utf-8 -*-
"""
Created on Wed Nov 25 20:46:00 2015

@author: BurdenBear
"""

import json
from Bigfish.utils.common import Currency


###################################################################
class AccountManager:
    """交易账户对象"""
    
    def __init__(self, capital_base=100000, name="", currency=Currency("USD"), leverage=1):
        self.__capital_base = capital_base
        self.__name = name
        self.__currency = currency
        self.__leverage = leverage
        self.initialize()
    
    def initialize(self):
        self.__capital_net = self.__capital_base
        self.__capital_cash = self.__capital_base
        self.__records = []
    
    def set_captital_base(self, captital_base):
        self.__capital_base = captital_base
        self.initialize
        
    def is_margin_enough(self, price):
        """判断账户保证金是否足够"""
        return(self.__capital_cash * self.__leverage >= price)
            
    def update_deal(self, deal):
        self.__capital_cash += deal.profit
        self.__records.append({'x':deal.time+deal.time_msc/(10**6),'y':self.__capital_cash/self.__capital_base})
    
    def get_profit(self):
        return(json.dumps(self.__records))
        