
# coding: utf-8

# In[1]:


import baostock as bs
import pandas as pd
import numpy as np
import talib as ta
import matplotlib.pyplot as plt
import KlineService
import BaoStockUtil
import math
import datetime
from scipy import integrate

from RSI import DayRSI,WeekRSI,MonthRSI,SixtyMinRSI
from concurrent.futures import ThreadPoolExecutor, as_completed
from Stock import Stock
import dbutil


from IPython.core.debugger import set_trace

#算积分用的节点数
INTEGRATE_CALC_RANGE = 4

RSI_OVER_BUY = 80
RSI_OVER_SELL = 20
RSI_OVER_BUY_12 = 75
RSI_OVER_SELL_12 = 25
RSI_OVER_BUY_24 = 70
RSI_OVER_SELL_24 = 30
RSI_MIDDLE = 50
#日线超卖区域积分阈值
RSI_INTE_OVERSELL_THRESHOLD_DAY = 50


# In[3]:


def findLatestRSIDate(period):
    mydb = dbutil.connectDB()
    collection = mydb[chooseRSICollection(period)]
    cursor = collection.find().sort("date",-1).limit(1)
    df =  pd.DataFrame(list(cursor))
    if df.empty:
        return "1970-01-01"
    return df["date"][0]

def clearRSI(period):
    mydb = dbutil.connectDB()
    collection = mydb[chooseRSICollection(period)]
    collection.delete_many({})
    indexes = collection.index_information()
    if "code_1_date_1" in indexes.keys():
        collection.drop_index( "code_1_date_1" )
        
def createIndex(period):
    mydb = dbutil.connectDB()
    collection = mydb[chooseRSICollection(period)]
    collection.create_index( [("code", 1), ("date",1)])

def integrateValues(valuesArray):
    return integrate.trapz(valuesArray, x=None, dx=1.0, axis=-1)
    
##
#  从数据库读指定日期RSI数据
#
#
def readRSI(period, stockCode, startDate, endDate):
    mydb = dbutil.connectDB()
    collection = mydb[chooseRSICollection(period)]
    if type(startDate) == str:
        startDate = datetime.datetime.strptime(startDate + "T00:00:00.000Z", "%Y-%m-%dT%H:%M:%S.000Z")
        endDate = datetime.datetime.strptime(endDate + "T23:59:59.000Z", "%Y-%m-%dT%H:%M:%S.000Z")
    cursor = collection.find({"code":stockCode,"date":{"$gte":startDate,"$lte":endDate}})
    df =  pd.DataFrame(list(cursor))
    return df
    
##
#  写RSI数据库
#
#
def writeRSIToDB(period, stockCode, stockName, rsi_df):
    dataList = []
    for index,rsi in rsi_df.iterrows():
        rsiDate = rsi['date']
        if period == "day":
            rsiObj = DayRSI(stockCode, stockName)
        elif period == "week":
            rsiObj = WeekRSI(stockCode, stockName)
        elif period == "month":
            rsiObj = MonthRSI(stockCode, stockName)
        elif period == "5m":
            rsiObj = FiveMinRSI(stockCode, stockName)
        elif period == "15m":
            rsiObj = FiftyMinRSI(stockCode, stockName)
        elif period == "30m":
            rsiObj = ThirtyMinRSI(stockCode, stockName)
        elif period == "60m":
            rsiObj = SixtyMinRSI(stockCode, stockName)

        rsiObj.date = rsiDate
        rsiObj.rsi_6 = rsi['rsi_6']
        rsiObj.rsi_12 = rsi['rsi_12']
        rsiObj.rsi_24 = rsi['rsi_24']
        rsiObj.overBuy = rsi['overBuyFlag']
        rsiObj.overSell = rsi['overSellFlag']
        
        dataList.append(rsiObj.__dict__)
        
    mydb = dbutil.connectDB()
    collection = mydb[chooseRSICollection(period)]
    if len(dataList) > 0:
        collection.insert_many(dataList)
    else:
        raise RuntimeError("RSI数据为空")


def computeStockRSI(period, stockCode, stockName, startDate, endDate):
    try:
#       compute1 = datetime.datetime.now().timestamp()
        df = KlineService.readStockKline(stockCode, period, startDate, endDate)
#       compute2 = datetime.datetime.now().timestamp()
#       print("read stockLine:", compute2 - compute1)
        if df.empty:
            return False
        if period == "day":
            # 剔除日线停盘数据
            df = df[df['tradeStatus'] == '1']
        rsi_df = computeRSI(df)
#       compute3 = datetime.datetime.now().timestamp()
#       print("compute rsi:", compute3 - compute2)
        writeRSIToDB(period, stockCode, stockName, rsi_df)
#       compute4 = datetime.datetime.now().timestamp()
#       print("write to db:", compute4 - compute3)
        return True
    except BaseException as e:
        print ("download " + stockCode + " error:" + str(e))
        return False

##
#  选择不同的Kline Collection
#
def chooseRSICollection(period):
    periodRSICollection = {
        "day" : "RSI_Day",
        "week" : "RSI_Week",
        "month" : "RSI_Month",
        "5m" : "RSI_5m",
        "15m" : "RSI_15m",
        "30m" : "RSI_30m",
        "60m" : "RSI_60m"
    }
    return periodRSICollection.get(period)


def computeRSI(klineDataFrame):
    rsi_12days = ta.RSI(klineDataFrame['closePrice'],timeperiod=12)
    rsi_6days = ta.RSI(klineDataFrame['closePrice'],timeperiod=6)
    rsi_24days = ta.RSI(klineDataFrame['closePrice'],timeperiod=24)
    
    rsiFrame = pd.DataFrame(klineDataFrame, columns=["date"])
    rsiFrame['rsi_6'] = rsi_6days
    rsiFrame['rsi_12'] = rsi_12days
    rsiFrame['rsi_24'] = rsi_24days
    ##添加参考线位置
    rsiFrame['overBuy'] = RSI_OVER_BUY
    rsiFrame['overSell'] = RSI_OVER_SELL
    rsiFrame['middle'] = RSI_MIDDLE

    # RSI超卖和超买
    rsi_buy_position = rsiFrame['rsi_12'] > RSI_OVER_BUY_12
    rsi_sell_position = rsiFrame['rsi_12'] < RSI_OVER_SELL_12
    rsiFrame.loc[rsi_buy_position[(rsi_buy_position == True) & (rsi_buy_position.shift() == False)].index, 'overBuyFlag'] = 'Yes'
    rsiFrame.loc[rsi_sell_position[(rsi_sell_position == True) & (rsi_sell_position.shift() == False)].index, 'overSellFlag'] = 'Yes'
    return rsiFrame


##
#  计算自起始日期起的RSI
#
#
def computeAllRSIDataOfPeriod(period, startDate):
#     currtime = datetime.datetime.now().timestamp()
    print("begin clear RSI period:", period)
    clearRSI(period)
    print("cleared RSI period:", period)
#     time1 = datetime.datetime.now().timestamp()
#     print("clear finished:",time1 - currtime)
    stockDict = KlineService.allStocks()
#     time2 = datetime.datetime.now().timestamp()
#     print("read stocks finished:",time2 - time1)
    endDate = str(datetime.date.today())
    jobStart = datetime.datetime.now().timestamp()
    
    processCount = 0
    failCount = 0
    jobTotal = len(stockDict)
    '''
    #起线程池来跑，单线程太慢了, 事实证明慢个鬼
    executor = ThreadPoolExecutor(max_workers=1)
    funcVars = []
    for key,stock in stockDict.items():
        #指数没有分钟线，调过指数的RSI分钟线计算
        if period.endswith("m") and (key.startswith("sh.000") or  key.startswith("sz.399")):
            continue
        funcVars.append([period, key, stock["name"], startDate, endDate])
    
    all_task = [executor.submit(computeStockRSI, funcVar[0], funcVar[1], funcVar[2], funcVar[3], funcVar[4]) 
                for funcVar in funcVars]
    for future in as_completed(all_task):
        processCount = processCount + 1
        if not future.result():
            failCount = failCount + 1
        if processCount % 100 == 0 and processCount > 0:
            print ("rsi process:", processCount, " of ", jobTotal ," failed:", failCount)
    '''
    for key,stock in stockDict.items():
        processCount = processCount + 1
        #指数没有分钟线，调过指数的RSI分钟线计算
        if period.endswith("m") and (key.startswith("sh.000") or  key.startswith("sz.399")):
            continue
        result = computeStockRSI(period, key, stock["name"], startDate, endDate)
        if not result:
            failCount = failCount + 1
        if processCount % 100 == 0 and processCount > 0:
            print ("rsi process:", processCount, " of ", jobTotal ," failed:", failCount)
            
    jobFinished = datetime.datetime.now().timestamp()
    createIndex(period)
    print("write all stock RSI to db finished, cost:", jobFinished - jobStart)
    return True

##
#  计算指定日期的RSI积分
#
#
def computeAllRSIDataIntegrate(period, specifiedDateStr, includeST):
    BaoStockUtil.customLogin()
    specifiedDate = datetime.datetime.strptime(specifiedDateStr, "%Y-%m-%d")
    today = datetime.date.today()
    #如果把时间设成未来，自动调成今天
    if specifiedDate > datetime.datetime.today():
        specifiedDate = datetime.date.today()
    #避免跨年问题，直接从去年开始取
    startDate = specifiedDate - datetime.timedelta(days = 365)
    #取交易日列表，用作倒推周期使用
    rs = bs.query_trade_dates(start_date=datetime.datetime.strftime(startDate, "%Y-%m-%d"), end_date = specifiedDate)
    BaoStockUtil.customLogout()
    if rs.error_code != '0':
        raise RuntimeError("交易日api调用失败了:" + rs.error_code)
    tradeDates = []
    while (rs.error_code == '0') & rs.next():
        row = rs.get_row_data()
        if row[1] == "1":
            tradeDates.append(row[0])
    if len(tradeDates) == 0:
        raise RuntimeError("取不到最新的交易日")
    
    #若期望计算的日期比库里RSI最新日期还晚，数据不全待补齐
    rsiLatestDate = findLatestRSIDate(period)
    rsiLatestDateStr = datetime.datetime.strftime(rsiLatestDate, "%Y-%m-%d")
    if rsiLatestDate < specifiedDate:
        raise RuntimeError(specifiedDateStr + " 的 " + period + " RSI的数据不存在，待补齐数据")
    
    #找到指定日期以及rsi存量数据最近日期在交易日周期的序号
    specifiedDateIndex = tradeDates.index(specifiedDateStr)
            
    if specifiedDateIndex == -1:
        raise RuntimeError(specifiedDateStr + " 可能不是交易日")
    daysBefore = computeRSIDataStartTradeDateRange(period, specifiedDateStr)
    startDateIndex = specifiedDateIndex - daysBefore
    
    #起始日期index负数，说明rsi数据不够
    if startDateIndex < 0:
        raise RuntimeError(period + " rsi数据不够")
    
    startDateStr = tradeDates[startDateIndex]
    print("compute rsi tradeDates from ", startDateStr, "to", specifiedDateStr)
    
    processCount = 0
    failCount = 0
    startDateIndex = -1
    dictStocks = KlineService.allStocks()
    klineDataFrame = KlineService.readAllStockKline(period, specifiedDateStr, specifiedDateStr)
    klineDataFrame = klineDataFrame.set_index("code")
    klineDict = klineDataFrame.to_dict('index')
    jobTotal = len(dictStocks)
    rsiValueArrs = []
    for i in range(0, 6):
        rsiValueArrs.append([])
    
    for key,stock in dictStocks.items():
        processCount = processCount + 1
        #指数没有分钟线，跳过指数的RSI分钟线计算
        if period.endswith("m") and stock.stockType != 1:
            continue
        #如果不计算ST，跳过
        if not includeST and stock["isST"]:
            continue
        #退市股就不要算了
        if "退" in stock["name"]:
            continue
        #科创板不达门槛没法买，不看
        if key.startswith("sh.68"):
            continue
        try:
            rsiDF = readRSI(period, key, startDateStr, specifiedDateStr)
            rsiCount = len(rsiDF)
            if rsiCount < INTEGRATE_CALC_RANGE:
                raise RuntimeError("积分计算节点不够")
            rsiValueArrs[0].append(key)
            rsiValueArrs[1].append(stock["name"])
            rsiValueArrs[2].append(klineDict[key]["closePrice"])
            #取最近的数据用于计算积分
            rsiValueArrs[3].append(rsiDF["rsi_6"][rsiCount - INTEGRATE_CALC_RANGE : rsiCount])
            rsiValueArrs[4].append(rsiDF["rsi_12"][rsiCount - INTEGRATE_CALC_RANGE : rsiCount])
            rsiValueArrs[5].append(rsiDF["rsi_24"][rsiCount - INTEGRATE_CALC_RANGE : rsiCount])
        except BaseException as e:
            failCount = failCount + 1
            print ("compute rsi integrate " + key + " error:" + str(e))
        if processCount % 100 == 0 and processCount > 0:
            print ("compute rsi integrate process:", processCount, " of ", jobTotal ," failed:", failCount)
    
    
    rsi6Arr = np.array(rsiValueArrs[3]).reshape(-1, INTEGRATE_CALC_RANGE)
    rsi6InteArr = integrateValues(rsi6Arr)
    rsi12Arr = np.array(rsiValueArrs[4]).reshape(-1, INTEGRATE_CALC_RANGE)
    rsi12InteArr = integrateValues(rsi12Arr)
    rsi24Arr = np.array(rsiValueArrs[5]).reshape(-1, INTEGRATE_CALC_RANGE)
    rsi24InteArr = integrateValues(rsi24Arr)
    
    rsiInteDF = pd.DataFrame()
    rsiInteDF["code"] = rsiValueArrs[0]
    rsiInteDF["name"] = rsiValueArrs[1]
    rsiInteDF["closePrice"] = rsiValueArrs[2]
    rsiInteDF["rsi_inte_6"] = rsi6InteArr
    rsiInteDF["rsi_inte_12"] = rsi12InteArr
    rsiInteDF["rsi_inte_24"] = rsi24InteArr
    
    return rsiInteDF
    

#算出计算本周期下指定数据需要的起始交易日
#每个交易日一共4小时，所以取4小时为一天，而不是24小时
#每个计算周期一共至少需要4个节点，分钟线RSI统一除以4*60=240分钟算出所需计算数据天数，最少为一天
#日线不用除分钟
## TODO 周线没想好怎么算，更别说月线了。
def computeRSIDataStartTradeDateRange(period, specifiedDate):
    daysBefore = 0
    if period.endswith("m"):
        daysBefore = math.ceil(INTEGRATE_CALC_RANGE * (int(period.replace("m", "")) + 1) / (60 * 4))
    elif period == "day":
        daysBefore = INTEGRATE_CALC_RANGE
    else:
        raise RuntimeError("周期有误")
    return daysBefore

