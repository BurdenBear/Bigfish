# -*- coding: utf-8 -*-
"""
Created on Wed Nov 25 20:41:04 2015

@author: BurdenBear
"""

class dataGenerator:
    """fetch data from somewhere and put dataEvent into eventEngine
        数据生成器
    Attrs:
        __engine:the eventEngine where dataEvent putted into        
        __symols:symbol of assets
        __start_time:start time of data
        __end_time:end tiem of data
        __time_frame_bits:bits contain information of which time frame to use
    """
    
    def __init__(self, engine, symbols, start_time, end_time, time_frame_bits):
        self.__engine = engine
        self.__symbols = symbols
        self.__start_time = start_time
        self.__end_time = end_time
        self.__time_frame_bits = time_frame_bits
    
    def __start():
        
    
    