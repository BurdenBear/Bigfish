# -*- coding: utf-8 -*-
from Bigfish.strategy.backtesting import backtesting

if __name__ == '__main__':
    symbol = '000001.SZ'
    sourcePath = './Bigfish/technical/signal'    
    strategyName = 'demoStrategy'
    backtesting(symbol, strategyName, sourcePath)