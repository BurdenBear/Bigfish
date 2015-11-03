# -*- coding: utf-8 -*-
def demoStrategy(fastLength = 10 , slowLength = 20): 
    #维护fastLengh内最高最低价以及出场
    if totalbar > fastLength:
        highestFast = max(High[(-fastLength-1):-1])
        lowestFast = min(Low[(-fastLength-1):-1])
        if (High[-1  ] > highestFast)and(marketposition < 0):
            cover(highestFast, 1)
        if (Low[-1]  < lowestFast)and(marketposition > 0):
            sell(lowestFast, 1)
    #维护slowLengh内最高最低价以及入场
    if totalbar > slowLength:
        highestSlow = max(High[(-slowLength-1):-1])
        lowestSlow = min(Low[(-slowLength-1):-1])
        if (High[-1] > highestSlow) and (marketposition == 0):
            buy(highestSlow,1)
        if (Low[-1] < lowestSlow) and (marketposition == 0):
            short(lowestSlow,1)