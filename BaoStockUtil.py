
# coding: utf-8

# In[1]:


import baostock as bs

bsLoggedIn = False

def customLogin():
    global bsLoggedIn
    if not bsLoggedIn:
        bs.login()
        bsLoggedIn = True
def customLogout():
    global bsLoggedIn
    if bsLoggedIn:
        bs.logout()
        bsLoggedIn = False

