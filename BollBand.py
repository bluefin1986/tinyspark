
# coding: utf-8

# In[ ]:


class BollBand(object):
    code = None
    name = None
    date = None
    upper = 0
    middle = 0
    lower = 0
    closePrice = 0
    overBuy = False
    overSell = False
    def __init__(self,code,name):
        self.code = code
        self.name = name
        
    def __str__(self):
        return '(%s %s %s %s)' %(self.code, self.name, self.date, self.closePrice)

class DayBollBand(BollBand):
    def __str__(self):
        return '(%s %s 日线布林（%s）：%s)' %(self.code, self.name, self.date, self.closePrice)
class WeekBollBand(BollBand):
    def __str__(self):
        return '(%s %s 周线布林（%s）：%s)' %(self.code, self.name, self.date, self.closePrice)
class MonthBollBand(BollBand):
    def __str__(self):
        return '(%s %s 月线布林（%s）：%s)' %(self.code, self.name, self.date, self.closePrice)
class FiveMinBollBand(BollBand):
    def __str__(self):
        return '(%s %s 5分钟线布林（%s）：%s)' %(self.code, self.name, self.date, self.closePrice)
class FiftyMinBollBand(BollBand):
    def __str__(self):
        return '(%s %s 15分钟线布林（%s）：%s)' %(self.code, self.name, self.date, self.closePrice)
class ThirtyMinBollBand(BollBand):
    def __str__(self):
        return '(%s %s 30分钟线布林（%s）：%s)' %(self.code, self.name, self.date, self.closePrice)
class SixtyMinBollBand(BollBand):
    def __str__(self):
        return '(%s %s 小时线布林（%s）：%s)' %(self.code, self.name, self.date, self.closePrice)

