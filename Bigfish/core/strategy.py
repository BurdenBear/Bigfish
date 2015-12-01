# -*- coding: utf-8 -*-

#系统模块
import inspect
import copy

#自定义模块
from Bigfish.event.handle import BarEventHandle
from Bigfish.utils.ast import LocalInjector
from Bigfish.utils.common import deque
#math包里没这个函数，自己写个
def sign (n):
    if abs(n) < 0.0000001:
        return 0
    elif n > 0:
        return 1
    elif n < 0:
        return -1
       
#%%策略容器，在初始化时定制一策略代码并在Onbar函数中运行他们
########################################################################
class Strategy:    
    ATTRS_MAP = {"period":"time_frame", "symbols":"symbols", "start":"start_time", "end":"end_time", "maxlen":"max_length" }  
    #----------------------------------------------------------------------
    def __init__(self, engine, name, code):
        """Constructor""" 
        self.name = name
        self.engine = engine
        self.time_frame = None
        self.symbols = set()
        self.start_time = None
        self.end_time = None
        self.event_handles = {}
        #TODO
        self.time_frame_bits = 0
        
        #将策略容器与对应代码文件关联   
        self.bind_code_to_strategy(code)
        
        #是否完成了初始化
        self.initCompleted = False
        #在字典中保存Open,High,Low,Close,Volumn，CurrentBar，MarketPosition，
        #手动为exec语句提供local命名空间
        self.__locals_ = {
                    'sell':self.engine.sell, 
                    'short':self.engine.short, 
                    'buy':self.engine.buy, 
                    'cover':self.engine.cover,
                    'marketposition':self.engine.get_positions(),
                    'currentcontracts':self.engine.get_currentcontracts(),
                    'datas':self.engine.get_datas()
                   }
        
        #在这里或者在Setting中还需添加额外的字典管理方法
        #为策略容器中所用的策略（序列和非序列）创建相应缓存变量并将名字加入字典
    #----------------------------------------------------------------------   
    #将策略容器与策略代码关联
    def bind_code_to_strategy(self, code):
        def get_parameter_default(paras, name, check, default):
            para = paras.get(name, None)
            if para:
                temp = para.default
                if temp == inspect._empty:
                    #TODO未给定值的处理
                    return(default)
                elif check(temp):
                    return(temp)
                else:
                    raise KeyError("变量%s所赋值不合法", name) 
            else:
                return(default)
        def get_time_frame_bits(time_frame):
            #TODO ---
            pass
        def get_global_attrs(locals_):
            for name,attr in self.ATTRS_MAP:
                setattr(self, attr, locals_.get(name))
                
        locals_ = {}           
        exec(code,copy.copy(self.__locals),locals_)
        get_global_attrs(locals_)
        to_inject = []    
        for k , v in locals_.items():
            if inspect.isfunction(v):
                paras = inspect.signature(v).parameters
                data_handler = get_parameter_default(para, "data_handler", lambda x:isinstance(x,bool), True)
                if not data_handler:
                    continue
                custom = get_parameter_default(paras, "custom", lambda x:isinstance(x,bool), True)                               
                if not custom:
                    #TODO加入真正的验证方法
                    symbols = get_parameter_default(paras, "symbols", lambda x:True, self.symbols)                   
                    time_frame = get_parameter_default(paras, "timeframe", lambda x:True, self.time_frame)
                    max_length = get_parameter_default(paras, "maxlen", lambda x: isinstance(int)and(x>0), None)
                    #TODO 处理max_length                    
                    self.time_frame_bits |= get_time_frame_bits(time_frame)
                    #XXX 是否有封装的必要                    
                    #self.event_handles[k] = BarEventHandle(self.engine, symbols[0])
                    for field in ["open","high","low","close","time","volume"]:
                        self.__locals_[field] = self.__locals_["datas"][symbols[0]][field]                        
                    to_inject[k] = self.__locals_
                else:
                    #自定义事件处理
                    pass
        print("<%s>信号添加成功" % name)
        return(True)
    
    #----------------------------------------------------------------------
    def onTick(self, tick):
        """行情更新"""
        raise NotImplementedError
      
    #----------------------------------------------------------------------    
    def onTrade(self, trade):
        """交易更新"""
        """trade.direction = 1 买单,trade.direction = -1 卖单
           marketposition = 1 持多仓,-1持空仓,0为空仓
        """
        marketPosition = self.marketPosition
        if trade.direction * marketPosition >= 0:
                self.currentContracts += trade.volume
                self.marketPosition = trade.direction
        else:
                currentConstracts = self.currentContracts - trade.volume
                self.currentConstracts = abs(currentConstracts)
                self.marketPosition = marketPosition * sign(currentConstracts)
    
    #----------------------------------------------------------------------
    def onOrder(self, order):
        pass            
    
    #----------------------------------------------------------------------
    def onBar(self, bar):
        """K线数据更新"""
        self.listOpen.append(bar.open)
        self.listHigh.append(bar.high)
        self.listLow.append(bar.low)
        self.listClose.append(bar.close)
        self.listVolume.append(bar.volume)        
        self.listTime.append(bar.time)
        next(self.onBarGeneratorInstance)

    #----------------------------------------------------------------------
    def start(self):
        """
        启动交易
        这里是最简单的改变self.trading
        有需要可以重新实现更复杂的操作
        """
        self.trading = True
        self.engine.writeLog(self.name + u'开始运行')
        
    #----------------------------------------------------------------------
    def stop(self):
        """
        停止交易
        同上
        """
        self.trading = False
        self.engine.writeLog(self.name + u'停止运行')
        
    #----------------------------------------------------------------------
    def loadSetting(self, setting):
        """
        载入设置
        setting通常是一个包含了参数设置的字典
        """
        pass

    #----------------------------------------------------------------------
    def cancelOrder(self, orderRef):
        """撤单"""
        self.engine.cancelOrder(orderRef)
        
    #----------------------------------------------------------------------
    def cancelStopOrder(self, so):
        """撤销停止单"""
        self.engine.cancelStopOrder(so)
    
        