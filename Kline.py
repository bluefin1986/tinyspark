
# coding: utf-8

# In[9]:


#K线父类
class Kline(object):
    code = None
    name = None
    date = None
    openPrice = 0
    highPrice = 0
    lowPrice = 0
    closePrice = 0
    #成交量（累计 单位：股）
    volumn = 0
    #成交额（单位：人民币元）
    amount = 0
    #复权状态(1：后复权， 2：前复权，3：不复权）
    adjustFlag = None
    
    def __init__(self,code,name):
        self.code = code
        self.name = name
        
    def __str__(self):
        return '(%s %s %s %s)' %(self.code, self.name, self.date, self.closePrice)

#日K线
class DayKline(Kline):
    #换手率
    turn = 0
    #交易状态(1：正常交易 0：停牌）
    tradeStatus = 1
    #涨跌幅（百分比）
    changePercent = 0
    #昨收
    preClosePrice = 0
    #是否ST股，1是，0否
    isST = 0
    
    def __str__(self):
        return '(%s %s 日线收盘（%s）：%s)' %(self.code, self.name, self.date, self.closePrice)
    
#周K线
class WeekKline(Kline):
    def __str__(self):
        return '(%s %s 周线收盘（%s）：%s)' %(self.code, self.name, self.date, self.closePrice)
    
#月K线
class MonthKline(Kline):
    def __str__(self):
        return '(%s %s 月线收盘（%s）：%s)' %(self.code, self.name, self.date, self.closePrice)

#5分钟线
class FiveMinKline(Kline):
    def __str__(self):
        return '(%s %s 5分钟收盘（%s）：%s)' %(self.code, self.name, self.date, self.closePrice)
#30分钟线
class ThirtyMinKline(Kline):
    def __str__(self):
        return '(%s %s 5分钟收盘（%s）：%s)' %(self.code, self.name, self.date, self.closePrice)
#60分钟线
class SixtyMinKline(Kline):
    def __str__(self):
        return '(%s %s 5分钟收盘（%s）：%s)' %(self.code, self.name, self.date, self.closePrice)


# In[8]:


dayk = Kline("sz.000001", "深发展")
print (dayk.name)

