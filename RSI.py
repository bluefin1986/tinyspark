
# coding: utf-8

# In[1]:


# RSI指标父类
class RSI(object):
    code = None
    name = None
    date = None
    rsi_6 = 0
    rsi_12 = 0
    rsi_24 = 0
    overSell = False
    overBuy = False
    
    def __init__(self,code,name):
        self.code = code
        self.name = name
        
    def __str__(self):
        return '(%s %s %s %s %s %s overSell:%s overBuy:%s)' %(self.code, self.name, self.date, 
                              self.rsi_6, self.rsi_12, self.rsi_24, overSell, overBuy)

#日线RSI
class DayRSI(RSI):
    def __str__(self):
        return '(日线RSI:%s %s %s %s %s %s overSell:%s overBuy:%s)' %(self.code, self.name, self.date, 
                              self.rsi_6, self.rsi_12, self.rsi_24, overSell, overBuy)
#周线RSI
class WeekRSI(RSI):
    def __str__(self):
        return '(周线RSI:%s %s %s %s %s %s overSell:%s overBuy:%s)' %(self.code, self.name, self.date, 
                              self.rsi_6, self.rsi_12, self.rsi_24, overSell, overBuy)
#月线RSI
class MonthRSI(RSI):
    def __str__(self):
        return '(月线RSI:%s %s %s %s %s %s overSell:%s overBuy:%s)' %(self.code, self.name, self.date, 
                              self.rsi_6, self.rsi_12, self.rsi_24, overSell, overBuy)
#5分钟线RSI
class FiveMinRSI(RSI):
    def __str__(self):
        return '(5分钟线RSI:%s %s %s %s %s %s overSell:%s overBuy:%s)' %(self.code, self.name, self.date, 
                              self.rsi_6, self.rsi_12, self.rsi_24, overSell, overBuy)
#15分钟线RSI
class FiftyMinRSI(RSI):
    def __str__(self):
        return '(15分钟线RSI:%s %s %s %s %s %s overSell:%s overBuy:%s)' %(self.code, self.name, self.date, 
                              self.rsi_6, self.rsi_12, self.rsi_24, overSell, overBuy)
#30分钟线RSI
class ThirtyMinRSI(RSI):
    def __str__(self):
        return '(30分钟线RSI:%s %s %s %s %s %s overSell:%s overBuy:%s)' %(self.code, self.name, self.date, 
                              self.rsi_6, self.rsi_12, self.rsi_24, overSell, overBuy)
#小时线RSI
class SixtyMinRSI(RSI):
    def __str__(self):
        return '(小时线RSI:%s %s %s %s %s %s overSell:%s overBuy:%s)' %(self.code, self.name, self.date, 
                              self.rsi_6, self.rsi_12, self.rsi_24, overSell, overBuy)

