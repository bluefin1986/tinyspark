
# coding: utf-8

# In[ ]:


class Stock(object):
    code = None
    name = None
    tradeStatus = 1
    stockType = None
    isST = False
    
    def __init__(self,code,name):
        self.code = code
        self.name = name
        
    def __str__(self):
        return '(%s %s %s)' %(self.code, self.name, self.tradeStatus)

