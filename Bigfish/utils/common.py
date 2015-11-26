# -*- coding: utf-8 -*-
"""
Created on Thu Nov 26 10:46:33 2015

@author: BurdenBear
"""

###################################################################
class Currency:
    """货币对象"""
    def __init__(self, name=""):
        self.__name = name

###################################################################
class Assert:
    """资产对象"""
    def __init__(self, symbol):
        self.symbol = symbol
        #TODO 资产的其他信息，如滑点、手续费等信息
        #将以json的形式存于文件或数据库中
        
    