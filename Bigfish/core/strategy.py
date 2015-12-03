# -*- coding: utf-8 -*-

#系统模块
from functools import partial
import ast
import inspect

#自定义模块
from Bigfish.event.handle import BarEventHandle
from Bigfish.utils.ast import LocalsInjector
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
    def __init__(self, engine, id_, name, code):
        """Constructor""" 
        self.__id = id_        
        self.name = name
        self.engine = engine
        self.time_frame = None
        self.symbols = set()
        self.start_time = None
        self.end_time = None
        self.event_handlers = {}
        #TODO
        self.time_frame_bits = 0
        
        #将策略容器与对应代码文件关联   
        self.bind_code_to_strategy(code)
        
        #是否完成了初始化
        self.initCompleted = False
        #在字典中保存Open,High,Low,Close,Volumn，CurrentBar，MarketPosition，
        #手动为exec语句提供local命名空间
        self.__locals_ = {
                    'sell':partial(self.engine.sell, strategy = self.__id),
                    'short':partial(self.engine.short, strategy = self.__id),
                    'buy':partial(self.engine.buy, strategy = self.id_),
                    'cover':partial(self.engine.cover, strategy = self.__id),
                    'marketposition':self.engine.get_positions(),
                    'currentcontracts':self.engine.get_currentcontracts(),
                    'datas':self.engine.get_datas()
                   }
        
        #在这里或者在Setting中还需添加额外的字典管理方法
        #为策略容器中所用的策略（序列和非序列）创建相应缓存变量并将名字加入字典
    def get_id(self):
        return(self.__id)
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
        exec(code,{},locals_)
        get_global_attrs(locals_)
        to_inject = {}
        events = {}
        temp = {key:'__globals["%s"]' % key for key in self.__locals_.keys()}
        for k , v in locals_.items():
            if inspect.isfunction(v):
                paras = inspect.signature(v).parameters
                data_handler = get_parameter_default(paras, "data_handler", lambda x:isinstance(x,bool), True)
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
                    #self.event_handlers[k] = BarEventHandle(self.engine, symbols[0])
                    for field in ["open","high","low","close","time","volume"]:
                        temp[field] = '__globals["datas"]["%s"]["%s"]' % (symbols[0], field)
                    to_inject[k] = temp
                    #TODO支持多品种事件             
                    events[k] = get_data_event(symbols)
                else:
                    #TODO自定义事件处理
                    pass
        injector = LocalsInjector(to_inject)
        ast_ = ast.parse(code)
        injector.visit(ast_)
        exec(compile(ast_,'<string>',mode='exec'), self.__locals_+[], locals_)
        for key, event in events():
             self.event_handlers[key] = locals_[key]()
             self.engine.register_event(event,self.event_handlers[key].__next__)
        print("<%s>信号添加成功" % self.name)
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
        for handler in self.event_handlers.values():
            handler.close()
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
    
        