# -*- coding: utf-8 -*-
"""
Created on Thu Nov 26 10:46:33 2015

@author: BurdenBear
"""
from collections import UserList
from collections import deque

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
###################################################################
class DictLike():
    __slots__=[]
    def to_dict(self):
        cls = self.__class__.__name__
        return ({slot.replace('__',''):getattr(self,slot.replace('__','_%s__'%cls))
                for slot in self.__slots__})
    def __getitem__(self,key):
        return (getattr(self,key))
###################################################################
class HasID:
    """有自增长ID对象的通用方法"""
    __slots__=[]
    __AUTO_INC_NEXT = 0
    #XXX 是否把自增写入
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
###################################################################
class SeriesList(UserList):
    __MAX_LENGTH = 10000    
    def __init__(self, initlist=None, max_length=None):
        self.max_length = None
        if max_length:
            if isinstance(max_length, int):
                if max_length > 0:
                    self.max_length = max_length
        else:
            self.max_length = self.__class__.__MAX_LENGTH
        if not self.max_length:
            raise (ValueError("参数max_length的值不合法"))        
        if len(initlist) > self.max_length:
            super().__init__(list(reversed(initlist[-max_length:])))
        else:
            super().__init__(list(reversed(initlist)))
        self.last = len(self.data)
        self.full = self.last == self.max_length
        self.last %= self.max_length
    def append(self,item):
        if not self.full:
            self.data.append(item)
            self.last += 1
            if self.last == self.max_length:
                self.full = True
                self.last = 0
        else:
            self.data[self.last] = item
            self.last = (self.last+1)%self.max_length
    def __getitem__(self, i): 
        if not self.full:
            return self.data[self.last-i-1]
        else:
            return self.data[(self.last-i-1+self.max_length)%self.max_length]
    def __setitem__(self, i, item): raise(TypeError("SeriesList is read-only"))
    def __delitem__(self, i): raise(TypeError("SeriesList is read-only"))