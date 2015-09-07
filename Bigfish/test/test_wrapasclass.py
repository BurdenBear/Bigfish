# -*- coding: utf-8 -*-
"""
Created on Fri Aug 28 13:57:24 2015

@author: morrison
"""
import types
import time

class timethis:
    def __init__(self,func):
        wraps(func)(self)
    
    def __call__(self,*args,**kwargs):
        self.start = time.time()
        self.str = self.__wrapped__(*args,**kwargs)
        self.end = time.time()
        self.runtime = self.end - self.start
        return self
'''    
    def __get__(self,instance,cls):
        if instance is None:
            return self
        else:
            return types.MethodType(self,instance)
'''
@timethis
@
def count(n):
    while n > 0:
        n-=1
    return 0
        

if __name__ == '__main__':
    t1=count(1000000)
    t2=count(1000000)