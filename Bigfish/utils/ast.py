# -*- coding: utf-8 -*-
"""
Created on Wed Nov  4 11:58:21 2015

@author: BurdenBear
"""

import ast
import inspect

class NameLower(ast.NodeVisitor):
    def __init__(self, lowered_names):
        self.lowered_names = lowered_names
    
    def visit_FunctionDef(self, node):
        code = '__globals = globals()\n'
        code += '\n'.join("{0} = __globals['{0}']
        code_ast = ast.parse(code, mode = 'exec')
        
        #Inject new statements into the function body
        node.body[:0] = code_ast.body
        
        #Save the function object
        self.func = node
        
#Decorator that turns global names into locals
def lower_names(func, *namelist):
    src = inspect.getsource(func)
    if src.startswith((' ','\t')):
        src = 'if 1:\n' + src
    top = ast.parse(src, mode= 'exec')
    
    nl = NameLower(namelist)
    nl.visit(top)
    
    temp = {}
    exec(compile(top,'','exec'), {}, temp)
    
    func.__code__ = temp[func.__name__].__code__
    return func

class LocalsInjector():
    """向函数中注入局部变量，参考ast.NodeVisitor"""
    def __init__(self, to_inject={}):
        self.__locals_ = __locals_
        self.__depth = 0
        self.__to_inject = to_inject
        
    def visit(self, node):
        self.__depth += 1
        #print("<deep>:<%d>"%self.__deep, node)
        method = 'visit_' + node.__class__.__name__
        visitor = getattr(self, method, self.generic_visit)
        visitor(node)
        self.__depth -= 1
        
    def visit_FunctionDef(self,node):
        if (self.__depth == 2) and (node.name in self.__to_inject):        
            print("function<%s> find!" % node.name)
            print(ast.dump(node))
            for name, value in self.__to_inject[node.name].items():
                                
        self.generic_visit(node)
        
    def generic_visit(self, node):
        """Called if no explicit visitor function exists for a node."""
        for field, value in iter_fields(node):
            if isinstance(value, list):
                for item in value:
                    if isinstance(item, AST):
                        self.visit(item)
            elif isinstance(value, AST):
                self.visit(value)