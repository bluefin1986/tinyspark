
# coding: utf-8

# In[2]:


import baostock as bs
import pandas as pd
import dbutil
from Stock import Stock
from datetime import datetime, date
from Kline import DayKline,WeekKline,MonthKline,SixtyMinKline
from IPython.core.debugger import set_trace

stocks = None

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
        
def queryStockName(stockCode):
    customLogin()
    #查股票名字
    #返回示例数据
    #code	code_name	ipoDate	outDate	type	status
    #sh.600000	浦发银行	1999-11-10		1	1
    rs = bs.query_stock_basic(code=stockCode)
    stockName = None
    if (rs.error_code == '0') & rs.next():
        stockName = rs.get_row_data()[1]
    if stockName == None:
        raise RuntimeError("无此股票代码：", stockCode)
    return stockName

##
#  下载日K线数据
#  stockCode 股票代码
#  startDate 起始时间
#  endDate   结束时间
#
def downloadDailyStockKline(stockCode, startdate, enddate):
    return downloadPeriodStockKline("day", stockCode, startdate, enddate)

##
#  下载指定周期的K线数据
#  period 周期
#  stockCode 股票代码
#  startDate 起始时间
#  endDate   结束时间
#
def downloadPeriodStockKline(period, stockCode, startDate, endDate):
    frequency = chooseFrequency(period)
    customLogin()
    stockDict = allStocks()
    stockName = stockDict[stockCode]["name"]
    
    #要查的字段，各周期有些许不同
    queryFields = []
    queryFields.append("date")
    if period.endswith("m"):
        queryFields.append("time")
    queryFields.append("open")
    queryFields.append("high")
    queryFields.append("low")
    queryFields.append("close")
    queryFields.append("volume")
    queryFields.append("amount")
    queryFields.append("adjustflag")
    if period == "day" or period == "week" or period == "month":
        queryFields.append("turn")
        queryFields.append("pctChg")
    if period == "day":
        queryFields.append("preclose")
        queryFields.append("tradestatus")
        queryFields.append("isST")
    queryFields = ",".join(queryFields)
    adjustFlag = "2"
#     queryFields = "date,open,high,low,close,preclose,volume,amount,adjustflag,turn,tradestatus,pctChg,isST"
    #### 获取沪深A股历史K线数据 ####
    # 详细指标参数，参见“历史行情指标参数”章节；“分钟线”参数与“日线”参数不同。
    # 分钟线指标：date,time,code,open,high,low,close,volume,amount,adjustflag
    rs = bs.query_history_k_data_plus(stockCode, queryFields,
        start_date=str(startDate), end_date=str(endDate),
        frequency=frequency, adjustflag=adjustFlag)
    if rs.error_code != '0':
        raise RuntimeError("读" + stockCode + " 数据失败了")
    ##下载下来的数据，存数据库去
    writeKlineToDb(period, stockCode, stockName, rs)
    return True

##
#  写K线数据库
#
#
def writeKlineToDb(period, stockCode, stockName, resultSet):
    dataList = []
    #分钟线多了个time字段，偏移量+1
    offset = 1 if period.endswith("m") else 0
    while (resultSet.error_code == '0') & resultSet.next():
        # 获取一条记录，将记录合并在一起
#         data_list.append(rs.get_row_data())
        row = resultSet.get_row_data()
    
        kline = None
        recordDate = None
        
        if period == "day":
            kline = DayKline(stockCode, stockName)
        elif period == "week":
            kline = WeekKline(stockCode, stockName)
        elif period == "month":
            kline = MonthKline(stockCode, stockName)
        elif period == "5m":
            kline = FiveMinKline(stockCode, stockName)
        elif period == "15m":
            kline = FiftyMinKline(stockCode, stockName)
        elif period == "30m":
            kline = ThirtyMinKline(stockCode, stockName)
        elif period == "60m":
            kline = SixtyMinKline(stockCode, stockName)
        else:
            raise RuntimeError("还不支持这个周期：" + period)
#         recordDate = datetime.strptime(row[0], "%Y-%m-%d")
        
        kline.openPrice = row[1 + offset]
        kline.highPrice = row[2 + offset]
        kline.lowPrice = row[3 + offset]
        kline.closePrice = row[4 + offset]
        kline.volume = row[5 + offset]
        kline.amount = row[6 + offset]
        kline.adjustflag = row[7 + offset]
#         set_trace()
        # 日K、月K、周K有专有属性
        if period == "day" or period == "week" or period == "month":
            recordDate = datetime.strptime(row[0 + offset], "%Y-%m-%d")
            kline.turn = row[8 + offset]
            kline.changePercent = row[9 + offset]
        else:
            recordDate = datetime.strptime(row[0 + offset], "%Y%m%d%H%M%S000")
        # 日K专有属性
        if period == "day":
            kline.preClosePrice = row[10]
            kline.tradeStatus = row[11]
            kline.isST = row[12]
        kline.date = recordDate
        
        dataList.append(kline.__dict__)
    mydb = dbutil.connectDB()
    collection = mydb[chooseKlineCollection(period)]
    if len(dataList) > 0:
        collection.insert_many(dataList)
        if period == "day":
            latestKlineDay = dataList[len(dataList) - 1]
            query = {"code":latestKlineDay["code"]}
            newvalues = { "$set": { "isST": latestKlineDay["isST"] == "1"} }
            mydb["Stock"].update_one(query, newvalues)
    else:
        raise RuntimeError("数据为空")

##
#  选择不同的周期，调api用的
#
def chooseFrequency(period):
    frequency = {
        "day" : "d",
        "week" : "w",
        "month" : "m",
        "5m" : "5",
        "15m" : "15",
        "30m" : "30",
        "60m" : "60"
    }
    return frequency.get(period)

##
#  选择不同的Kline Collection
#
def chooseKlineCollection(period):
    periodKlineCollection = {
        "day" : "Kline_Day",
        "week" : "Kline_Week",
        "month" : "Kline_Month",
        "5m" : "Kline_5m",
        "15m" : "Kline_15m",
        "30m" : "Kline_30m",
        "60m" : "Kline_60m"
    }
    return periodKlineCollection.get(period)

##
# 读取所有股票K线数据
# 
#
def readAllStockKline(period, startDate, endDate):
    return readStockKline(None, period, startDate, endDate)
        
##
#  从数据库读取K线数据，转DataFrame
#  startDate、endDate在日线级别以上时，自动拼接成结束日23:59:59
#
def readStockKline(code, period, startDate, endDate):
    mydb = dbutil.connectDB()
    cursor = None
    periodCollection = chooseKlineCollection(period)
    startDate = datetime.strptime(startDate + "T00:00:00.000Z", "%Y-%m-%dT%H:%M:%S.000Z")
    endDate = datetime.strptime(endDate + "T23:59:59.000Z", "%Y-%m-%dT%H:%M:%S.000Z")
    query  = {"date":{"$gte":startDate, "$lte":endDate}}
    if code != None and len(code) > 0:
        query["code"] = code
    cursor = mydb[chooseKlineCollection(period)].find(query)
    df =  pd.DataFrame(list(cursor))
    return df

def downloadAllStocks(tradeDate):
    customLogin()
#     set_trace()
#     stock_rs = bs.query_all_stock(tradeDate)
    stock_rs = bs.query_stock_basic()
    stock_df = stock_rs.get_data()
    dataList = []
    for index,stock in stock_df.iterrows():
        stockObj = Stock(stock["code"], stock["code_name"])
        stockObj.stockType = stock["type"]
        dataList.append(stockObj.__dict__)
    mydb = dbutil.connectDB()
    mydb["Stock"].delete_many({})
    mydb["Stock"].insert_many(dataList)
    customLogout()
    
    return True

## 
# 获取指定日期的指数、股票数据
#
def allStocks():
    global stocks
    if stocks != None:
        return stocks
    mydb = dbutil.connectDB()
    cursor = mydb["Stock"].find({})
    
    df = pd.DataFrame(list(cursor))
    df = df.set_index("code")
#     set_trace()
    stocks = df.to_dict('index')
    return stocks
        

def latestTradeDate():
    customLogin()
#     set_trace()
    rs = bs.query_trade_dates(start_date=date.today().replace(day=1), end_date = date.today())
    if rs.error_code != '0':
        raise RuntimeError("交易日api调用失败了:" + rs.error_code)
    tradeDates = []
    while (rs.error_code == '0') & rs.next():
        row = rs.get_row_data()
        if row[1] == "1":
            tradeDates.append(row[0])
#     set_trace()
    if len(tradeDates) == 0:
        raise RuntimeError("取不到最新的交易日")
    now = datetime.now()
    set_trace()
    tradeDatesCount = len(tradeDates)
    ## 因为baoStock的日K数据更新时间是 17：30， 所以如果在18点前启动，可能取不到当天数据，交易日向前推一天
    if (now.hour < 18 and tradeDatesCount > 1):
        return tradeDates[tradeDatesCount - 2]
    else:
        return tradeDates[len(tradeDates) - 1]

def downloadAllKlineDataOfSingleDay(date):
    customLogin()
    stockDict = allStocks()
    downloadedCount = 0
    
    for key in stockDict:
        downloadDailyStockKline(key, date, date)
        downloadedCount = downloadedCount + 1
        if downloadedCount % 100 == 0 and downloadedCount > 0:
            print ("process:", downloadedCount, " of ", len(stockDict) )
    customLogout()

def downloadAllKlineDataOfPeriod(period, startDate):
    print("begin clear Kline period:", period, "since ", startDate)
    clearKlineData(period, startDate)
    print("begin download Kline period", period, "since ", startDate)
    customLogin()
    endDate = ""
    downloadedCount = 0
    failCount = 0
    indexCount = 0
    
    stockDict = allStocks()
    totalCount = len(stockDict)
    for key,stock in stockDict.items():
        downloadedCount = downloadedCount + 1
        #指数没有分钟线，跳过
        if period.endswith("m") and stock["stockType"] != "1":
            indexCount = indexCount + 1
            continue
        try:
            downloadPeriodStockKline(period, key, startDate, endDate)
        except BaseException as e:
            failCount = failCount + 1
            print ("download " + key + " error:" + str(e))
        
        if downloadedCount % 100 == 0 and downloadedCount > 0:
            print ("download process:", downloadedCount, " of ", totalCount ," failed:", failCount, " passed index:", indexCount)
    customLogout()
    createIndex(period)

def createIndex(period):
    mydb = dbutil.connectDB()
    collection = mydb[chooseKlineCollection(period)]
    collection.create_index( [("code", 1), ("date",1)])
    
def clearKlineData(period, startDate):
    mydb = dbutil.connectDB()
    collection = mydb[chooseKlineCollection(period)]
    startDate = datetime.strptime(startDate + "T00:00:00.000Z", "%Y-%m-%dT%H:%M:%S.000Z")
    collection.delete_many({"date":{"$gte":startDate}})
    indexes = collection.index_information()
    if "code_1_date_1" in indexes.keys():
        collection.drop_index( "code_1_date_1" )
    

