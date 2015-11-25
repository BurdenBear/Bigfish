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

    
            
        
        