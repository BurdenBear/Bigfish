# -*- coding: utf-8 -*-
"""
Created on Fri Nov 27 22:42:54 2015

@author: BurdenBear
"""
from Bigfish.utils.common import deque

class EventHandle():
    
    def __init__():
        raise (NotImplementedError)
        
    def handle_data():
        raise (NotImplementedError)    

class BarEventHandle(EventHandle):
    def __init__(self, engine, symbol):
        self.__func = None
    
    def set_func(self, func):
        self.__func = func
        
    def handle_data(self, context):
        self.__handle_generator.send(context)
        
    def __handle_generator(self):
        
        while True:
            self.__func()
            
class TickEventHandle():
    #TODO    
    pass