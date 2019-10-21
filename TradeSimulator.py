
# coding: utf-8

# In[4]:


import datetime
from Account import *
from Trade import *
from StockHolding import *
from Stock import *
from RSICompute import *
from Strategy import *
import uuid
import KlineService
import RSICompute
from IPython.core.debugger import set_trace
import dbutil

#初始化指定数量的账号
def initAccount(acctCount, equity):
    if acctCount <= 0:
        raise RuntimeError("初始化账户数得大于0")
    dateStr = datetime.datetime.strftime(datetime.datetime.now(), "%m%d")
    mydb = dbutil.connectDB()
    collection = mydb["Account"]
    dataList = []
    for i in range(0, acctCount):
        newAcct = Account(str(uuid.uuid1()).replace("-",""), dateStr + "account" + str(i + 1))
        newAcct.initiatedEquity = equity
        newAcct.equity = equity
        dataList.append(newAcct.__dict__)
    collection.insert_many(dataList)
    return True
    
def loadAccounts():
    mydb = dbutil.connectDB()
    collection = mydb["Account"]
    cursor = collection.find({})
    df = pd.DataFrame(list(cursor))
    return df

##
# 执行某一天的交易
# specifiedDate 日期
# strategy 交易策略
#
def executeTrade(specifiedDate, strategy):
    #取所有的
    dfKline = KlineService.readAllStockKline("day", specifiedDate, specifiedDate)
    if dfKline.empty:
        raise RuntimeError("没有%s的K线数据，无法交易" % specifiedDate)
    dfAcct = loadAccounts()
    if dfAcct.empty:
        raise RuntimeError("交易账户还没有初始化")
    stocks = findStocksByRSI("day", specifiedDate, strategy, False)
    return stocks

##
# 计算出RSI策略下的操作股票列表
#
#
def findStocksByRSI(period, specifiedDate, strategy, includeST):
    df = RSICompute.computeAllRSIDataIntegrate(period, specifiedDate, includeST)
    df = df[df["rsi_inte_6"] <= strategy.RSI_INTE_OVERSELL_THRESHOLD_DAY].sort_values(by=['rsi_inte_6'])
    if df.empty:
        raise RuntimeError("%s 这天没的股票推荐" % specifiedDate)
    #把选中股票当周期价格找出来
    stockDict = KlineService.readAllStockKline(period, specifiedDate, specifiedDate)\
        .set_index("code").to_dict('index')
    stocks = []
    for index,rsiInte in df.iterrows():
        stocks.append(stockDict[rsiInte.code])
    return stocks


# initAccount(10, 100000)
rsiStrategy = RSIStrategy()
print(executeTrade("2019-10-14", rsiStrategy))


str(uuid.uuid1()).replace("-","")

