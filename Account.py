
# coding: utf-8

# In[1]:


class Account(object):
    acctId = None
    acctName = None
    #起始资金
    initiatedEquity = 0.0
    #资产总值
    equity = 0.0
    #可用金额
    balanceAvailable = 0.0
    #盈利
    profits = 0.0
    
    def __init__(self, acctId, acctName):
        self.acctId = acctId
        self.acctName = acctName
        
    def __str__(self):
        print('(%s %s %f %f)' % (self.acctId, self.acctName, self.equity, profits))

