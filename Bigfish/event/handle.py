# -*- coding: utf-8 -*-
"""
Created on Fri Nov 27 22:42:54 2015

@author: BurdenBear
"""
from Bigfish.utils.common import HasID
from Bigfish.event.event import EVENT_BAR_SYMBOL

#XXX以下几个可能删除掉
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
#-----------------------------------------------------------------------
class SymbolsListener(EventHandle, HasID):
    def __init__(self, engine, symbols, time_frame):
        self.__id = self.next_auto_inc()
        self.__symbols = {item:n for n,item in enumerate(symbols)}
        self.__count = len(symbols)
        self.__time_frame = time_frame
        self.__engine = engine
        self.__generator = None
        self.__gene_istance = None
        self.__handler = self.__handle()
    def get_id(self):
        return(self.__id)
    def set_generator(self, generator):
        self.__generator = generator
    def start(self):
        if self.__generator:
            self.__gene_istance = self.__generator()
            for symbol in self.__symbols.keys():
                    self.__engine.register_event(EVENT_BAR_SYMBOL[symbol][self.__time_frame],
                                           self.__handler.send)
            self.__handler.send(None)# start it
    def stop(self):
        if self.__generator:        
            for symbol in self.__symbols.keys():
                self.__engine.unregister_event(EVENT_BAR_SYMBOL[symbol][self.__time_frame],
                                         self.__handler.send)
            self.__gene_istance.close()
            self.__handler.close()# stop it
    def __handle(self):
        bits_ready = (1 << self.__count) - 1
        bits_now = 0
        while True:
            event = yield
            bar = event.content["data"]
            bits_now |= 1 << self.__symbols[bar.symbol]
            if bits_now == bits_ready:
                self.__gene_istance.__next__()
                bits_now = 0
    