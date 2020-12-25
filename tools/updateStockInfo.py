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

def getFromContinueCache (stockID):
    filename = "../info/%s_continue.txt" % (stockID,)
    if check_file (filename) == False:
        return {}
    file = open (filename, "r", encoding="utf-8")
    tmp = file.read ()
    file.close()
    return json.loads (tmp)

def saveContinueCache (stockID, info):
    filename = "../info/%s_continue.txt" % (stockID,)
    file = open (filename, "w", encoding="utf-8")
    file.writelines (json.dumps (info))
    file.close()

# 取得所有的股票清單
allstock = AllStockMgr.getAllStock ()
miss_qeps = 0
miss_turnover = 0
threeKey = "2020/12/25"

epsKey = "2020Q3"
turnOverKey = "2020/11"
sdKey = "2019"

del_dir ("cache")
check_dir ("cache")

for stockID, stock in allstock.items():
    # 載入暫存資料
    info = getFromCache (stockID)
    # 連續型的資料
    continueInfo = getFromContinueCache (stockID)
    # if len(info) != 0:
    #     continue
    # 為了寫資料方便, 暫時不抓沒資料的
    if stock.operationType == "":
        continue

    # 及時報價
    #print (NetStockInfo.getYahooRealtime (stockID, False))
    # 基本資料
    if "股本" not in info:
        info.update (NetStockInfo.getYahooBasic (stockID))

    # 每季EPS
    #print (NetStockInfo.getHistockQEPS (stockID))
    if "QEPS" not in info or epsKey not in info["QEPS"]:
        res, info["QEPS"] = NetStockInfo.getHistockQEPS (stockID)
        if res == False:
            print ("1")
            continue
        if epsKey not in info["QEPS"]:
            miss_qeps += 1
            print (stock.name, "還未有", epsKey, "EPS")
        else:
            print (epsKey, json.dumps(info["QEPS"][epsKey]))

    # 每月營收
    #print (NetStockInfo.getHistockTurnOver (stockID))
    if "月營收" not in info or turnOverKey not in info["月營收"]:
        res, info["月營收"] = NetStockInfo.getHistockTurnOver (stockID)
        if res == False:
            print ("2")
            continue
        if turnOverKey not in info["月營收"]:
            miss_turnover += 1
            print (stock.name, "還未有", turnOverKey, "月營收")
        else:
            print (turnOverKey, json.dumps(info["月營收"][turnOverKey]))
    # 把每月營收 Copy 到連續資料中
    if "月營收" not in continueInfo:
        continueInfo["月營收"] = {}
    continueInfo["月營收"].update (info["月營收"])

    # 取得三大法人進出
    if "三大法人" not in info or threeKey != info["三大法人"][0]["date"]:
        res, info["三大法人"] = NetStockInfo.getHistockThree (stockID)
        if res == False:
            print ("4")
            continue
        if threeKey != info["三大法人"][0]["date"]:
            miss_turnover += 1
            print (stock.name, "還未有", threeKey, "三大法人")
        else:
            print (threeKey, json.dumps(info["三大法人"][0]))
    # 把三大法人資訊加入每日資料
    if "三大法人" not in continueInfo:
        continueInfo["三大法人"] = {}
    for tmp in info["三大法人"]:
        continueInfo["三大法人"][tmp["date"]] = tmp
    
    # 取得配股息進出 (每年一次，不會太頻繁)
    if "配股配息" not in info:
        res, info["配股配息"] = NetStockInfo.getHistockStockDivide (stockID)
        if res == False:
            continue
        if len(info["配股配息"]) > 0:
            print ("配股配息", json.dumps(info["配股配息"][0]))
        else:
            print (stock.name, "還未有配股配息")

    # 把資料存起來
    saveCache (stockID, info)
    saveContinueCache (stockID, continueInfo)

    #break


