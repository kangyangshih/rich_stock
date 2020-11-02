# 做及時的報價, 目前每一分鐘一次
# DESC : 2020/11/2

#---------------------------
# 載入所有 python 共用模組
#---------------------------
import sys
sys.path.append(r"c:\download\ranb_gametowner\python_module")
from utility import *
# 載入這個專案共用模組
sys.path.append (r"..\module")
from AllStockMgr import AllStockMgr
from NetStockInfo import NetStockInfo
import json

# 印出資訊
def printStockInfo (stockID, stock):
    # 取得及時報價
    info = NetStockInfo.getYahooRealtime (stockID, False)
    #print (info)
    res = "%s[%s] %s(%s) %.2f 量 : %s" % (
        # 名稱
        stock.name, 
        # 編號
        stock.id, 
        # 現價
        info["now_price"], 
        # 買入價
        stock.buyPrice if stock.holdPrice == 0 else stock.holdPrice,
        # 今天漲跌幅
        info["now_result"], 
        # 今日量能
        info["now_vol"]
    )
    # 回傳結果
    if stock.buyPrice * 1.02 > info["now_price"]:
        return 1, res
    elif stock.buyPrice * 1.1 < info["now_price"]:
        return 2, res
    else:
        return 0, res

# 取得想要監控的股票
allStock = AllStockMgr.getAllStock (True)
print (len(allStock))
# 持有的股票, 股性波動大的, 定存股型的
stockList = [{}, {}, {}]
for stockID, stock in allStock.items():
    # 要有買入價才會監控
    if stock.buyPrice == 0:
        continue
    # 如果是持有股, 先放在 0
    if stock.holdPrice != 0:
        stockList[0][stockID] = stock
    # 定存股放在最後
    elif stock.tag.find ("定存股") != -1:
        stockList[2][stockID] = stock
    # 一般區
    else:
        stockList[1][stockID] = stock

# 定時做監控
clear_console ()
# 持有的股票, 股性波動大的, 定存股型的
for index, info in enumerate (stockList):
    if index == 0:
        print ("========持有股========")
    elif index == 1:
        print ("========觀察股========")
    else:
        print ("========定存股========")
    # 印出內容
    buyList = []
    modifyList = []
    for stockID , stock in info.items():
        res, msg = printStockInfo (stockID, stock)
        if res == 1:
            buyList.append (msg)
        elif res == 2 and index == 2:
            pass
        else:
            modifyList.append (msg)
    print ("--- 可進場 ---")
    for msg in buyList:
        print (msg)
    print ("--- 等待中 ---")
    for msg in modifyList:
        print (msg)

