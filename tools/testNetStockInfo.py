# 載入所有 python 共用模組
import sys
sys.path.append(r"c:\download\ranb_gametowner\python_module")
from utility import *
# 載入這個專案共用模組
sys.path.append (r"..\module")
from AllStockMgr import AllStockMgr
from NetStockInfo import NetStockInfo
import json

# 取得所有的股票清單
allstock = AllStockMgr.getAllStock ()
for stockID, stock in allstock.items():
    if stockID != "3293":
        continue
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
    print (NetStockInfo.getHistockStockDivide (stockID))



