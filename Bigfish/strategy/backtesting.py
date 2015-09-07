# -*- coding: utf-8 -*-
#自定义模块
from .strategyEngine import *
from .backtestingEngine import *
#系统模块
from datetime import datetime
import time
# 回测脚本    
def backtesting(symbol,strategyClass,**kwargs):
 
    # 创建回测引擎
    be = BacktestingEngine()
    
    # 创建策略引擎对象
    se = StrategyEngine(be.eventEngine, be, backtesting=True)
    be.setStrategyEngine(se)
    
    endTime = kwargs.pop('endTime',datetime.fromtimestamp(int(time.time())))
    startTime = kwargs.pop('startTime',datetime(2015,8,20))
    
    # 初始化回测引擎
    be.connectWind()
    be.loadDataHistoryFromWind(symbol, startTime, endTime)
    
    
        
    # 创建策略对象
    setting = {}
    se.createStrategy(strategyClass.__name__, symbol, strategyClass, setting)
    
    # 启动所有策略
    se.startAll()
    
    # 开始回测
    be.startBacktesting()