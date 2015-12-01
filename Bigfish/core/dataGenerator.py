# -*- coding: utf-8 -*-
"""
Created on Wed Nov 25 20:41:04 2015

@author: BurdenBear
"""
from Bigfish.event.eventType import EVENT_BARDATA, TIME_FRAME, Event
import copy 

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
        self.__data_events = []
        
    def __get_datas(self, time_frame):
        """根据数据源的不同选择不同的实现"""
        raise(NotImplementedError)
        
    def __insert_datas(self, time_frame):
        datas = self.__get_datas(time_frame)
        temp = copy.copy(self.__data_events)
        self.__data_events = []
        cursor_d = 0
        cursor_t = 0
        length_d = len(datas)
        length_t = len(temp)
        #和之前的数据按结束时间进行归并
        while (cursor_d<length_d and cursor_t<length_t):
            data_d = datas[cursor_d]
            data_t = temp[cursor_t].content['data']
            if data_d.ctime + data_d.time_frame <= data_t.ctime + data_t.time_frame:
                self.__data_events.append(Event(type_=EVENT_BARDATA[time_frame], content={'data':data_d}))
                cursor_d += 1
            else:
                self.__data_events.append(temp[cursor_t])
                cursor_t += 1
        while (cursor_d<length_d):
            self.__data_events.append(Event(type_=EVENT_BARDATA[time_frame], content={'data':datas[cursor_d]}))
            cursor_d += 1
        while (cursor_t<length_t):
            self.__data_events.append(temp[cursor_t])
            cursor_t += 1
            
    def start(self):
        time_frame_bits = self.__time_frame_bits
        for time_frame in TIME_FRAME:
            if time_frame_bits & 1:
                self.__insert_events(time_frame)
            time_frame_bits >>= 1
        #回放数据
        for data_event in self.__data_events:
            self.__engine.put(data_event)
            
        
    
    