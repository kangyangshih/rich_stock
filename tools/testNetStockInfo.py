# 載入所有 python 共用模組
import sys
sys.path.append(r"..\..\ranb_gametowner\python_module")
from utility import *
# 載入這個專案共用模組
sys.path.append (r"..\module")
from AllStockMgr import AllStockMgr
from NetStockInfo import NetStockInfo
from StockDBMgr import StockDBMgr
import json

keywordList = [
    "除權基準日",
    "除息基準日",
    "除權息基準日",
]

# 取得所有的股票清單
allstock = AllStockMgr.getAllStock ()
for stockID, stock in allstock.items():
    # 取得今年度的配息日
    # 取得新聞
    #tmp, newsList = StockDBMgr.getNews (stockID)
    #for news in newsList:
    #    print (news["dateStr"], news["title"])
    #if stockID != "3293":
    #    continue
    # 及時報價
    #print (NetStockInfo.getYahooRealtime (stockID, False))
    # 每季EPS
    #print (NetStockInfo.getHistockQEPS (stockID))
    # 基本資料
    #print (NetStockInfo.getYahooBasic (stockID))
    # 每月營收
    #print (NetStockInfo.getHistockTurnOver (stockID))
    # 取得流動比 / 速動比
    #print (NetStockInfo.getHistockLSRate (stockID))
    # 取得30日三大法人
    #print (NetStockInfo.getHistockThree (stockID))
    # 取得配股配息
    #print (NetStockInfo.getHistockStockDivide (stockID))
    # 取得
    #break
    pass



