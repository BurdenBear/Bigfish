# -*- coding: utf-8 -*-

#系统模块
from functools import partial
import ast
import inspect

#自定义模块
from Bigfish.event.handle import SymbolsListener
from Bigfish.utils.ast import LocalsInjector
from Bigfish.utils.common import check_time_frame, HasID

#%%策略容器，在初始化时定制一策略代码并在Onbar函数中运行他们
########################################################################
class Strategy(HasID):    
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
        self.handlers = {}
        self.listeners = {}
        self.__context = {}      
        #是否完成了初始化
        self.initCompleted = False
        #在字典中保存Open,High,Low,Close,Volumn，CurrentBar，MarketPosition，
        #手动为exec语句提供local命名空间
        self.__locals_ = {
                    "sell":partial(self.engine.sell, strategy = self.__id),
                    "short":partial(self.engine.short, strategy = self.__id),
                    "buy":partial(self.engine.buy, strategy = self.__id),
                    "cover":partial(self.engine.cover, strategy = self.__id),
                    "marketposition":self.engine.get_positions(),
                    "currentcontracts":self.engine.get_currentcontracts(),
                    "datas":self.engine.get_datas(),
                    "context":self.__context
                   }
        #将策略容器与对应代码文件关联   
        self.bind_code_to_strategy(code)
        
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
        def get_global_attrs(locals_):
            for name,attr in self.ATTRS_MAP.items():
                setattr(self, attr, locals_.get(name))               
        
        locals_ = {}
        globals_ = {}           
        exec(code,globals_,locals_)
        get_global_attrs(locals_)
        globals_.update(self.__locals_)
        globals_.update(locals_)
        self.engine.start_time = self.start_time
        self.engine.end_time = self.end_time
        check_time_frame(self.time_frame)
        to_inject = {}
        temp = {key:"__globals['%s']" % key for key in self.__locals_.keys()
                if key not in ['sell','buy','short','cover']}
        for key , value in locals_.items():
            if inspect.isfunction(value):
                paras = inspect.signature(value).parameters
                data_handler = get_parameter_default(paras, "data_handler", lambda x:isinstance(x,bool), True)
                if not data_handler:
                    continue
                custom = get_parameter_default(paras, "custom", lambda x:isinstance(x,bool), False)                               
                if not custom:
                    #TODO加入真正的验证方法
                    symbols = get_parameter_default(paras, "symbols", lambda x:True, self.symbols)                   
                    time_frame = get_parameter_default(paras, "timeframe", check_time_frame, self.time_frame)
                    max_length = get_parameter_default(paras, "maxlen", lambda x: isinstance(int)and(x>0), 0)                                    
                    self.engine.add_symbols(symbols,time_frame,max_length)
                    self.listeners[key] = SymbolsListener(self.engine, symbols, time_frame)
                    for field in ["open","high","low","close","time","volume"]:
                        temp[field] = "__globals['datas']['%s']['%s']['%s']" % (symbols[0], time_frame, field)
                    for field in ["buy","short","sell","cover"]:
                        temp[field] = "functools.partial(__globals['%s'],listener=%d)" % (field,self.listeners[key].get_id())
                    to_inject[key] = temp
                else:
                    #TODO自定义事件处理
                    pass
        injector = LocalsInjector(to_inject)
        ast_ = ast.parse(code)
        injector.visit(ast_)
        exec(compile(ast_,"<string>",mode="exec"), globals_, locals_)
        for key in to_inject.keys():
             self.listeners[key].set_generator(locals_[key])
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
        pass
    
    #----------------------------------------------------------------------
    def start(self):
        """
        启动交易
        这里是最简单的改变self.trading
        有需要可以重新实现更复杂的操作
        """
        self.trading = True
        for listener in self.listeners.values():
            listener.start()
        self.engine.writeLog(self.name + u'开始运行')
        
    #----------------------------------------------------------------------
    def stop(self):
        """
        停止交易
        同上
        """
        self.trading = False
        for listener in self.listeners.values():
            listener.stop()
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
    
        