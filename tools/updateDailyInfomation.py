# 更新每日資訊
import sys
sys.path.append(r"c:\download\ranb_gametowner\python_module")
from utility import *
#WebViewMgr.debugMode ()
# 載入這個專案共用模組
sys.path.append (r"..\module")
from AllStockMgr import AllStockMgr
from NetStockInfo import NetStockInfo
import json
import csv

# 季 EPS
epsKey = "2020Q3"
#epsKey = "2020Q4"
# 月營收
turnOverKey = "2021/02"
#turnOverKey = "2021/03"
# 股利分配
sdKey = "2019"

# 取得內容
# isPage : 是不是股 -> 張
def getCSVRowNumber (value, isPage=False):
    #print ("~~~[getCSVRowNumber] "+ value)
    value = value.strip (" ")
    if value == "":
        return "0"
    if value == "0":
        return "0"
    if value == "--":
        return "0"
    if value == "---":
        return "0"
    if value.find (",") != -1:
        value = value.replace (",", "")
    if isPage == False:
        #print (isPage, value)
        return value
    else:
        #print (isPage, "%.0f" % (int(value)/1000,))
        return "%.0f" % (int(value)/1000,)

# 取得所有的股票清單
allstock = AllStockMgr.getAllStock ()

#------------------------------------------------
print ("=== [更新基本資料] ===")
# 計算還有幾家沒有 QEPS、月營收
leave = 0
for stockID, stock in allstock.items():
    # 載入暫存資料
    info = getFromCache ("../info/%s.txt" % (stockID,), {})
    if "QEPS" not in info or epsKey not in info["QEPS"]:
        continue
    leave += 1
print ("[QEPS %s] 更新進度 %s/%s" % (epsKey, leave, len(allstock)))
leave = 0
for stockID, stock in allstock.items():
    # 載入暫存資料
    info = getFromCache ("../info/%s.txt" % (stockID,), {})
    if "月營收" not in info or turnOverKey not in info["月營收"]:
        continue
    leave += 1
print ("[月營收 %s] 更新進度 %s/%s" % (turnOverKey, leave, len(allstock)))
# 更新基本資料
for stockID, stock in allstock.items():
    # 載入暫存資料
    info = getFromCache ("../info/%s.txt" % (stockID,), {})

    #------------------------------------------
    # 基本資料
    #if "股本" not in info: 
    if "產業類別" not in info:
        info.update (NetStockInfo.getYahooBasic (stockID))

    #------------------------------------------
    # 每季EPS
    #print (NetStockInfo.getHistockQEPS (stockID))
    if "QEPS" not in info or epsKey not in info["QEPS"]:
        if "QEPS" not in info:
            info["QEPS"] = {}
        res, tmp = NetStockInfo.getHistockQEPS (stockID)
        if res == False:
            print ("1")
            continue
        # 做多出來的更新動作 (舊的不刪)
        info["QEPS"].update (tmp)
        if epsKey not in info["QEPS"]:
            print (stock.name, "還未有", epsKey, "EPS")
        else:
            print (epsKey, json.dumps(info["QEPS"][epsKey]))

    #------------------------------------------
    # 每月營收
    #print (NetStockInfo.getHistockTurnOver (stockID))
    if "月營收" not in info or turnOverKey not in info["月營收"]:
        if "月營收" not in info:
            info["月營收"] = {}
        res, tmp = NetStockInfo.getHistockTurnOver (stockID)
        if res == False:
            print ("2")
            continue
        info["月營收"].update (tmp)
        if turnOverKey not in info["月營收"]:
            print (stock.name, "還未有", turnOverKey, "月營收")
        else:
            print (turnOverKey, json.dumps(info["月營收"][turnOverKey]))

    #------------------------------------------
    # 取得配股息進出 (每年一次，不會太頻繁)
    if "配股配息" not in info:
        if "配股配息" not in info:
            info["配股配息"] = {}
        res, tmp = NetStockInfo.getHistockStockDivide (stockID)
        if res == False:
            continue
        info["配股配息"].update (tmp)
        if len(info["配股配息"]) > 0:
            print ("配股配息", json.dumps(info["配股配息"][0]))
        else:
            print (stock.name, "還未有配股配息")

    #------------------------------------------
    # 計算 2020Q1、2020Q2、2020Q3 季營收
    tmpMap = {
        # 2020
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
    saveCache ("../info/%s.txt" % (stockID,), info)

#------------------------------------------------
# 更新三大法人
print ("=== [更新三大法人] ===")
# 先取得 ../tmp 下的 csv 檔案
filelist = get_dir_file_list ("../daily")
for filename in filelist:
    if filename.find ("ignore") != -1:
        continue
    #---------------------
    # 處理上櫃的內容
    if filename.find ("BIGD_") != -1:
        # 取得 threeKey
        print ("處理:", filename)
        purename = getPureFilename (filename)
        purename = purename[8:-4]
        #print (purename)
        threeKey = "2021/%s/%s" % (purename[:2], purename[-2:])
        if filename.find ("BIGD_109") != -1:
            threeKey = "2020/%s/%s" % (purename[:2], purename[-2:])
        print ("上櫃檔案, 日期:", threeKey)
        # 做開檔的的動作
        file = open (filename, "r", encoding="utf-8")
        rows = csv.reader(file, delimiter=',', quotechar='"')
        for row in rows:
            stockID = row[0]
            if row[0] not in allstock:
                continue
            # 載入暫存資料
            info = getFromCache ("../info/%s.txt" % (stockID,), {})
            if "三大法人" not in info:
                info["三大法人"] = {}
            #print ("~~ %s (%s) ~~~" % (allstock[stockID].name, stockID))
            #print (row)
            #print (row[10][:-4], row[13][:-4], row[16][:-4], row[19][:-4], row[23][:-4])
            tmp = {
                # 日期
                "date" : threeKey,
                # 外資
                "out_buy" : getCSVRowNumber(row[8], True),
                "out_sell" : getCSVRowNumber(row[9], True),
                "out" : getCSVRowNumber(row[10], True),
                # 投信
                "in_buy" : getCSVRowNumber(row[11], True),
                "in_sell" : getCSVRowNumber(row[12], True),
                "in" : getCSVRowNumber(row[13], True),
                # 自營商(自行買賣)
                "self_0_buy" : getCSVRowNumber(row[14], True),
                "self_0_sell" : getCSVRowNumber(row[15], True),
                "self_0" : getCSVRowNumber(row[16], True),
                # 自營商(避險)
                "self_1_buy" : getCSVRowNumber(row[17], True),
                "self_1_sell" : getCSVRowNumber(row[18], True),
                "self_1" : getCSVRowNumber(row[19], True),
                # 總計
                "total" : getCSVRowNumber(row[23], True),
            }
            #print (tmp)
            info["三大法人"][threeKey] = tmp
            # 做存入的動作
            saveCache ("../info/%s.txt" % (stockID,), info)
        file.close()

        # 要補沒有資料的部分
        tmp = {
            # 日期
            "date" : threeKey,
            # 外資
            "out_buy" : "0",
            "out_sell" : "0",
            "out" : "0",
            # 投信
            "in_buy" : "0",
            "in_sell" : "0",
            "in" : "0",
            # 自營商(自行買賣)
            "self_0_buy" : "0",
            "self_0_sell" : "0",
            "self_0" : "0",
            # 自營商(避險)
            "self_1_buy" : "0",
            "self_1_sell" : "0",
            "self_1" : "0",
            # 總計
            "total" : "0",
        }
        for stockID, stock in allstock.items():
            if stock.location != "上櫃":
                continue
            info = getFromCache ("../info/%s.txt" % (stockID,), {})
            if "三大法人" not in  info:
                info["三大法人"] = {}
            if threeKey not in info["三大法人"]:
                #print ("%s 在 %s 沒有三大法人資料，補空的進去" % (stock.name, threeKey))
                info["三大法人"][threeKey] = tmp
                saveCache ("../info/%s.txt" % (stockID,), info)

    #---------------------
    # 處理上巿內容
    if filename.find ("T86_ALL_") != -1:
        # 取得 threeKey
        print ("處理:", filename)
        purename = getPureFilename (filename)
        purename = purename[12:-4]
        #print (purename)
        threeKey = "2021/%s/%s" % (purename[:2], purename[-2:])
        if filename.find ("T86_ALL_2020") != -1:
            threeKey = "2020/%s/%s" % (purename[:2], purename[-2:])
        print ("上巿檔案 ALL, 日期:", threeKey)
        file = open (filename, "r", encoding="utf-8")
        rows = csv.reader(file, delimiter=',', quotechar='"')
        for row in rows:
            if len(row) == 0:
                continue
            stockID = row[0]
            if row[0] not in allstock:
                continue
            # 載入暫存資料
            info = getFromCache ("../info/%s.txt" % (stockID,), {})
            if "三大法人" not in info:
                info["三大法人"] = {}
            #print ("~~ %s (%s) ~~~" % (allstock[stockID].name, stockID))
            #print (row)
            #print (row[10][:-4], row[13][:-4], row[16][:-4], row[19][:-4], row[23][:-4])
            tmp = {
                # 日期
                "date" : threeKey,
                # 外資
                "out_buy" : getCSVRowNumber(row[2], True),
                "out_sell" : getCSVRowNumber(row[3], True),
                "out" : getCSVRowNumber(row[4], True),
                # 投信
                "in_buy" : getCSVRowNumber(row[8], True),
                "in_sell" : getCSVRowNumber(row[9], True),
                "in" : getCSVRowNumber(row[10], True),
                # 自營商(自行買賣)
                "self_0_buy" : getCSVRowNumber(row[12], True),
                "self_0_sell" : getCSVRowNumber(row[13], True),
                "self_0" : getCSVRowNumber(row[14], True),
                # 自營商(避險)
                "self_1_buy" : getCSVRowNumber(row[15], True),
                "self_1_sell" : getCSVRowNumber(row[16], True),
                "self_1" : getCSVRowNumber(row[17], True),
                # 總計
                "total" : getCSVRowNumber(row[18], True),
            }
            #print (tmp)
            info["三大法人"][threeKey] = tmp
            # 做存入的動作
            saveCache ("../info/%s.txt" % (stockID,), info)
        file.close()

        # 要補沒有資料的部分
        tmp = {
            # 日期
            "date" : threeKey,
            # 外資
            "out_buy" : "0",
            "out_sell" : "0",
            "out" : "0",
            # 投信
            "in_buy" : "0",
            "in_sell" : "0",
            "in" : "0",
            # 自營商(自行買賣)
            "self_0_buy" : "0",
            "self_0_sell" : "0",
            "self_0" : "0",
            # 自營商(避險)
            "self_1_buy" : "0",
            "self_1_sell" : "0",
            "self_1" : "0",
            # 總計
            "total" : "0",
        }
        for stockID, stock in allstock.items():
            if stock.location != "上巿":
                continue
            info = getFromCache ("../info/%s.txt" % (stockID,), {})
            if "三大法人" not in  info:
                info["三大法人"] = {}
            if threeKey not in info["三大法人"]:
                #print ("%s 在 %s 沒有三大法人資料，補空的進去" % (stock.name, threeKey))
                info["三大法人"][threeKey] = tmp
                saveCache ("../info/%s.txt" % (stockID,), info)
    #---------------------
    # 處理上巿內容
    if filename.find ("T86_ALLBUT0999_") != -1:
        # 取得 threeKey
        print ("處理:", filename)
        purename = getPureFilename (filename)
        purename = purename[19:-4]
        #print (purename)
        threeKey = "2021/%s/%s" % (purename[:2], purename[-2:])
        if filename.find ("T86_ALLBUT0999_2020") != -1:
            threeKey = "2020/%s/%s" % (purename[:2], purename[-2:])
        print ("上巿檔案 BUT0999, 日期:", threeKey)
        file = open (filename, "r", encoding="utf-8")
        rows = csv.reader(file, delimiter=',', quotechar='"')
        for row in rows:
            if len(row) == 0:
                continue
            stockID = row[0]
            if row[0] not in allstock:
                continue
            # 載入暫存資料
            info = getFromCache ("../info/%s.txt" % (stockID,), {})
            if "三大法人" not in info:
                info["三大法人"] = {}
            #print ("~~ %s (%s) ~~~" % (allstock[stockID].name, stockID))
            #print (row)
            #print (row[10][:-4], row[13][:-4], row[16][:-4], row[19][:-4], row[23][:-4])
            tmp = {
                # 日期
                "date" : threeKey,
                # 外資
                "out_buy" : getCSVRowNumber(row[2], True),
                "out_sell" : getCSVRowNumber(row[3], True),
                "out" : getCSVRowNumber(row[4], True),
                # 投信
                "in_buy" : getCSVRowNumber(row[8], True),
                "in_sell" : getCSVRowNumber(row[9], True),
                "in" : getCSVRowNumber(row[10], True),
                # 自營商(自行買賣)
                "self_0_buy" : getCSVRowNumber(row[12], True),
                "self_0_sell" : getCSVRowNumber(row[13], True),
                "self_0" : getCSVRowNumber(row[14], True),
                # 自營商(避險)
                "self_1_buy" : getCSVRowNumber(row[15], True),
                "self_1_sell" : getCSVRowNumber(row[16], True),
                "self_1" : getCSVRowNumber(row[17], True),
                # 總計
                "total" : getCSVRowNumber(row[18], True),
            }
            #print (tmp)
            info["三大法人"][threeKey] = tmp
            # 做存入的動作
            saveCache ("../info/%s.txt" % (stockID,), info)
        file.close()

        # 要補沒有資料的部分
        tmp = {
            # 日期
            "date" : threeKey,
            # 外資
            "out_buy" : "0",
            "out_sell" : "0",
            "out" : "0",
            # 投信
            "in_buy" : "0",
            "in_sell" : "0",
            "in" : "0",
            # 自營商(自行買賣)
            "self_0_buy" : "0",
            "self_0_sell" : "0",
            "self_0" : "0",
            # 自營商(避險)
            "self_1_buy" : "0",
            "self_1_sell" : "0",
            "self_1" : "0",
            # 總計
            "total" : "0",
        }
        for stockID, stock in allstock.items():
            if stock.location != "上巿":
                continue
            info = getFromCache ("../info/%s.txt" % (stockID,), {})
            if "三大法人" not in  info:
                info["三大法人"] = {}
            if threeKey not in info["三大法人"]:
                #print ("%s 在 %s 沒有三大法人資料，補空的進去" % (stock.name, threeKey))
                info["三大法人"][threeKey] = tmp
                saveCache ("../info/%s.txt" % (stockID,), info)

#------------------------------------------------
# 更新每日股價
print ("=== [更新每日股價] ===")
# 先取得 ../tmp 下的 csv 檔案
filelist = get_dir_file_list ("../daily")
#print (filelist)
for filename in filelist:
    if filename.find ("ignore") != -1:
        continue
    #---------------------
    # 處理上巿的內容
    if filename.find ("MI_INDEX_ALLBUT0999_") != -1:
        # 取得 dailyKey
        print ("處理:", filename)
        purename = getPureFilename (filename)
        purename = purename[-12:-4]
        year = purename[:4]
        month = purename[4:6]
        day = purename[6:]
        #print (purename)
        dailyKey = "%s/%s/%s" % (year, month, day)
        print ("上巿檔案, 日期:", dailyKey)
        # 做開檔的的動作
        file = open (filename, "r", encoding="utf-8")
        rows = csv.reader(file, delimiter=',', quotechar='"')
        for row in rows:
            if len(row) == 0:
                continue
            stockID = row[0]
            if row[0] not in allstock:
                continue
            diff = float (getCSVRowNumber(row[10]))
            tmp = {
                # 每日資訊
                "date" : dailyKey,
                # 量能 (從股數->張數)
                "vol" : int(getCSVRowNumber(row[2], True)),#int(int(getCSVRowNumber(row[2]))/1000),
                # 開盤價
                "start_price" : float (getCSVRowNumber(row[5])),
                # 最高價
                "high_price" : float (getCSVRowNumber(row[6])),
                # 最低價
                "low_price" : float (getCSVRowNumber(row[7])),
                # 收盤價
                "end_price" : float (getCSVRowNumber(row[8])),
                # 差價
                "diff" : float (getCSVRowNumber(row[10])),
            }
            tmp["pre_price"] = tmp["end_price"] - tmp["diff"]
            # 存進去資料庫中
            StockDBMgr.saveDaily (stockID, tmp)
        file.close()

        tmp = {
            # 每日資訊
            "date" : dailyKey,
            # 量能 (從股數->張數)
            "vol" : 0,
            # 開盤價
            "start_price" : 0,
            # 最高價
            "high_price" : 0,
            # 最低價
            "low_price" : 0,
            # 收盤價
            "end_price" : 0,
            # 差價
            "diff" : 0,
            # 前天價
            "pre_price" : 0,
        }
        # 要補沒有資料的部分
        for stockID, stock in allstock.items():
            if stock.location != "上巿":
                continue
            info = StockDBMgr.getDaily (stockID)
            if dailyKey != info[0]["date"]:
                print (stock.name, stock.id)
                # 存進去資料庫中
                StockDBMgr.saveDaily (stockID, tmp)

    #---------------------
    # 處理上櫃的內容 RSTA3104_1100129
    if filename.find ("RSTA3104_") != -1:
        # 取得 dailyKey
        print ("處理:", filename)
        purename = getPureFilename (filename)
        purename = purename[-8:-4]
        year = "2021"
        if filename.find ("RSTA3104_109") != -1:
            year = "2020"
        month = purename[:2]
        day = purename[2:]
        #print (purename)
        dailyKey = "%s/%s/%s" % (year, month, day)
        print ("上櫃檔案, 日期:", dailyKey)
        # 做開檔的的動作
        file = open (filename, "r", encoding="utf-8")
        rows = csv.reader(file, delimiter=',', quotechar='"')
        for row in rows:
            if len(row) == 0:
                continue
            stockID = row[0]
            if row[0] not in allstock:
                continue
            # 載入暫存資料
            #print (row[1], row[0])
            tmp = {
                # 每日資訊
                "date" : dailyKey,
                # 收盤價
                "end_price" : float (getCSVRowNumber(row[2])),
                # 差價
                "diff" : float (getCSVRowNumber(row[3])) if row[3].strip(" ") != "除權" and row[3].strip(" ") != "除息" and row[3].strip(" ") != "除權息" else None,
                # 開盤價
                "start_price" : float (getCSVRowNumber(row[4])),
                # 最高價
                "high_price" : float (getCSVRowNumber(row[5])),
                # 最低價
                "low_price" : float (getCSVRowNumber(row[6])),
                # 量能 (從股數->張數)
                "vol" : int(getCSVRowNumber(row[8], True)),#int(int(getCSVRowNumber(row[8]))/1000),
            }
            if tmp["diff"] != None:
                tmp["pre_price"] = tmp["end_price"] - tmp["diff"]
            else:
                tmp["pre_price"] = None
            # 存進去資料庫中
            StockDBMgr.saveDaily (stockID, tmp)
        file.close()

        tmp = {
            # 每日資訊
            "date" : dailyKey,
            # 量能 (從股數->張數)
            "vol" : 0,
            # 開盤價
            "start_price" : 0,
            # 最高價
            "high_price" : 0,
            # 最低價
            "low_price" : 0,
            # 收盤價
            "end_price" : 0,
            # 差價
            "diff" : 0,
            # 前天價
            "pre_price" : 0,
        }
        # 要補沒有資料的部分
        for stockID, stock in allstock.items():
            if stock.location != "上櫃":
                continue
            info = StockDBMgr.getDaily (stockID)
            if dailyKey != info[0]["date"]:
                print (stock.name, stock.id)
                # 存進去資料庫中
                StockDBMgr.saveDaily (stockID, tmp)

#------------------------------------
# 取得有開盤的日期
print ("=== [取得有開盤的日期] ===")
# 拿台泥來看
dayKeyList = StockDBMgr.getDayKey()
file = open ("../info/dailyList.txt", "w", encoding="utf-8")
file.writelines (json.dumps (dayKeyList))
file.close()
print (dayKeyList)

#------------------------------------
# 把沒有成交的個股，End Price 改成前次有價格
print ("=== [修改] ===")
for stockID, stock in allstock.items():
    # 取得資料
    infoList = StockDBMgr.getDaily (stockID)
    for index, info in enumerate (infoList):
        if info["end_price"] > 0:
            continue
        next_index = index+1
        while True:
            if next_index >= len(infoList):
                break
            if infoList[next_index]["end_price"] == 0:
                next_index += 1
                continue
            # 把價格做記錄的動作
            print ("%s[%s] %s 沒有交易資料, 拿 %s 補, 改為 %s" % (
                stock.name, 
                stock.id, 
                dayKey, 
                info[next_index]["date"]),
                info[next_index]["end_price"]),
            )
            info[index]["start_price"] = info[next_index]["end_price"]
            info[index]["high_price"] = info[next_index]["end_price"]
            info[index]["low_price"] = info[next_index]["end_price"]
            info[index]["end_price"] = info[next_index]["end_price"]
            info[index]["pre_price"] = info[next_index]["end_price"]
            # 強制做更新的動作
            StockDBMgr.saveDaily (stockID, info[index]["pre_price"], True)
            break