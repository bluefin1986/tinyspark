
# coding: utf-8

# In[ ]:


class Stock(object):
    code = None,
    name = None,
    tradeStatus = 1
    
    def __init__(self,code,name,tradeStatus):
        self.code = code
        self.name = name
        self.tradeStatus = tradeStatus
        
    def __str__(self):
        return '(%s %s %s)' %(self.code, self.name, self.tradeStatus)

