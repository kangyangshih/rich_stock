# DESC : 用來更新所有資料
# 載入所有 python 共用模組
import sys
sys.path.append(r"c:\download\ranb_gametowner\python_module")
from utility import *
#WebViewMgr.debugMode ()
# 載入這個專案共用模組
sys.path.append (r"..\module")
from AllStockMgr import AllStockMgr
from NetStockInfo import NetStockInfo
import json

def getFromCache (stockID):
    filename = "../info/%s.txt" % (stockID,)
    if check_file (filename) == False:
        return {}
    file = open (filename, "r", encoding="utf-8")
    tmp = file.read ()
    file.close()
    return json.loads (tmp)

def saveCache (stockID, info):
    filename = "../info/%s.txt" % (stockID,)
    file = open (filename, "w", encoding="utf-8")
    file.writelines (json.dumps (info))
    file.close()

# 取得所有的股票清單
allstock = AllStockMgr.getAllStock ()
for stockID, stock in allstock.items():
    # 載入暫存資料
    info = getFromCache (stockID)
    if len(info) != 0:
        continue
    # 及時報價
    #print (NetStockInfo.getYahooRealtime (stockID, False))
    # 基本資料
    #print (NetStockInfo.getYahooBasic (stockID))
    info.update (NetStockInfo.getYahooBasic (stockID))
    # 每季EPS
    #print (NetStockInfo.getHistockQEPS (stockID))
    res, info["QEPS"] = NetStockInfo.getHistockQEPS (stockID)
    if res == False:
        print ("1")
        continue
    # 每月營收
    #print (NetStockInfo.getHistockTurnOver (stockID))
    res, info["月營收"] = NetStockInfo.getHistockTurnOver (stockID)
    if res == False:
        print ("2")
        continue
    # 取得流動比 / 速動比
    #print (NetStockInfo.getHistockLSRate (stockID))
    res, info["流動/速動比"] = NetStockInfo.getHistockLSRate (stockID)
    if res == False:
        # 金融股都不會有這個值
        info["流動/速動比"] = None
        #print ("3")
    # 把資料存起來
    saveCache (stockID, info)


