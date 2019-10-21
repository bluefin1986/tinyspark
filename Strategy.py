
# coding: utf-8

# In[ ]:



class Strategy(object):
    #持仓比例，默认1即百分百
    holdingRatio = 1
    #最大持股数量，即可用资金最多用于购买多少支股票
    maxHoldingStocks = 4

    
class RSIStrategy(Strategy):
    RSI_OVER_BUY = 80
    RSI_OVER_SELL = 20
    RSI_OVER_BUY_12 = 75
    RSI_OVER_SELL_12 = 25
    RSI_OVER_BUY_24 = 70
    RSI_OVER_SELL_24 = 30
    #日线超卖区域积分阈值
    RSI_INTE_OVERSELL_THRESHOLD_DAY = 50
    #日线超买区域积分阈值
    RSI_INTE_OVERBUY_THRESHOLD_DAY = 300
    def isOverBuy(period):
        return False

    def isOverSell(period):
        return False

