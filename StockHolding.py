
# coding: utf-8

# In[1]:


class StockHolding(object):
    acctId = None
    stockCode = None
    stockName = None
    stockNums = 0
    stockPrice = 0.0
    cost = 0.0
    profits = 0.0
    tradeAbleNums = 0
    
    def _init_(self, acctId, stockCode, stockNums, stockPrice):
        self.acctId = acctId
        self.stockCode = stockCode
        self.stockNums = stockNums
        self.stockPrice = stockPrice

