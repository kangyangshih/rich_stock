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

def getCacheFilename (stockID):
    return "../info/%s.txt" % (stockID,)

# 取得所有的股票清單
allstock = AllStockMgr.getAllStock ()

# 季 EPS
epsKey = "2020Q3"
# 月營收
turnOverKey = "2020/12"
# 股利分配
sdKey = "2019"

for stockID, stock in allstock.items():
    # 載入暫存資料
    info = getFromCache (getCacheFilename(stockID), {})

    #------------------------------------------
    # 基本資料
    #if "股本" not in info: 
    if "產業類別" not in info:
        info.update (NetStockInfo.getYahooBasic (stockID))

    #------------------------------------------
    # 每季EPS
    #print (NetStockInfo.getHistockQEPS (stockID))
    if "QEPS" not in info or epsKey not in info["QEPS"]:
        res, info["QEPS"] = NetStockInfo.getHistockQEPS (stockID)
        if res == False:
            print ("1")
            continue
        if epsKey not in info["QEPS"]:
            print (stock.name, "還未有", epsKey, "EPS")
        else:
            print (epsKey, json.dumps(info["QEPS"][epsKey]))

    #------------------------------------------
    # 每月營收
    #print (NetStockInfo.getHistockTurnOver (stockID))
    if "月營收" not in info or turnOverKey not in info["月營收"]:
        res, info["月營收"] = NetStockInfo.getHistockTurnOver (stockID)
        if res == False:
            print ("2")
            continue
        if turnOverKey not in info["月營收"]:
            print (stock.name, "還未有", turnOverKey, "月營收")
        else:
            print (turnOverKey, json.dumps(info["月營收"][turnOverKey]))

    #------------------------------------------
    # 取得配股息進出 (每年一次，不會太頻繁)
    if "配股配息" not in info:
        res, info["配股配息"] = NetStockInfo.getHistockStockDivide (stockID)
        if res == False:
            continue
        if len(info["配股配息"]) > 0:
            print ("配股配息", json.dumps(info["配股配息"][0]))
        else:
            print (stock.name, "還未有配股配息")

    #------------------------------------------
    # 計算 2020Q1、2020Q2、2020Q3 季營收
    tmpMap = {
        "2020Q1" : ["2020/01", "2020/02", "2020/03"],
        "2020Q2" : ["2020/04", "2020/05", "2020/06"],
        "2020Q3" : ["2020/07", "2020/08", "2020/09"],
        "2020Q4" : ["2020/10", "2020/11", "2020/12"],
    }
    for key, valueList in tmpMap.items():
        if key not in info["QEPS"]:
            continue
        #print ("計算 %s 季營收 : %s" % (stock.name, key))
        total = 0
        for value in valueList:
            tmp = float (info["月營收"][value]["月營收"]) / 100000.0
            #print ("[%s] %.2f" % (value, tmp))
            total += tmp
        #print ("total : %.2f" % (total,))
        info["QEPS"][key]["MEPS"] = float(info["QEPS"][key]["EPS"])/3
        info["QEPS"][key]["季營收"] = total
        info["QEPS"][key]["平均月營收"] = total/3

    # 把資料存起來
    saveCache (getCacheFilename(stockID), info)



