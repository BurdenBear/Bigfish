# -*- coding: utf-8 -*-
from Bigfish.strategy.backtesting import backtesting
from Bigfish.strategy.demoStrategy import demoStrategy

if __name__ == '__main__':
    symbol = '000001.SZ'
    backtesting(symbol, demoStrategy)