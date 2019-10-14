
# coding: utf-8

# In[1]:


class Trade(object):
    
    tradeAcct = None
    stockCode = None
    stockName = None
    #买卖方向 0-买 1-卖
    tradeType = None
    #交易股数
    stockNums = 0
    #交易价格
    tradePrice = 0.0
    #交易金额
    tradeAmount = 0.0
    #交易手续费
    tradeFee = 0.0
    #交易日期
    tradeDate = None
    
    def __init__(self, tradeAcct, stockCode, tradeType, stockNums, tradePrice, tradeDate):
        self.tradeAcct = tradeAcct
        self.stockCode = stockCode
        self.tradeType = tradeType
        self.stockNums = stockNums
        self.tradePrice = tradePrice
        self.tradeAmount = tradePrice * stockNums
        self.tradeDate = tradeDate

