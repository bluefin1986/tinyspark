
# coding: utf-8

# In[ ]:


import pymongo
##
# 连接数据库，这里用的mongoDB
#
def connectDB():
    myclient = pymongo.MongoClient("mongodb://localhost:27017/")
    mydb = myclient["tinyspark"]
    return mydb

