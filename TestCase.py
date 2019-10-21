
# coding: utf-8

# In[ ]:


import KlineService
import RSICompute

# KlineService.downloadAllStocks("2019-10-16")
# KlineService.downloadAllKlineDataOfSingleDay("2019-09-30")
# KlineService.readStockKline("sh.600000", "day", "2018-01-01", "2019-09-29")
# KlineService.downloadAllKlineDataOfPeriod("60m", "2019-10-21")
# KlineService.downloadAllKlineDataOfPeriod("day", "2019-10-21")

# KlineService.readAllStockKline("day", "2019-10-11", "2019-10-11")


# RSICompute.downloadAllKlineDataOfSingleDay("2019-09-24")

# RSICompute.downloadAllKlineDataOfPeriod("day", "2017-01-01")
# RSICompute.downloadAllStocks("2019-09-23")
# dfStocks = KlineService.allStocks()

#计算RSI
# RSICompute.computeAllRSIDataOfPeriod("day", "2017-01-01")
# RSICompute.computeAllRSIDataOfPeriod("60m", "2018-01-01")

# RSICompute.computeAllRSIData("day", "2019-09-27")


# df600673 = readRSI("day", "sh.600673", "2019-09-24","2019-09-30")
# df002030 = readRSI("60m", "sz.002030", "2019-09-30","2019-09-30")
# valueArr = df600673["rsi_6"]
# valueArr = np.array(valueArr)
# set_trace()
# a = np.reshape(valueArr, (-1, len(df600673["rsi_6"])))
# integrateValues(a)

computeDate = "2019-10-21"
df = RSICompute.computeAllRSIDataIntegrate("day", computeDate, False)
df = df[df["rsi_inte_6"] <= RSICompute.RSI_INTE_OVERSELL_THRESHOLD_DAY].sort_values(by=['rsi_inte_6'])

df.to_csv("/Users/matt/Downloads/dayRSI_integrate_" + computeDate + ".csv")

