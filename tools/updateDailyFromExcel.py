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
import csv

def getCacheFilename (stockID):
    return "../info/daily_%s.txt" % (stockID,)

allstock = AllStockMgr.getAllStock ()

# 取得內容
def getCSVRowNumber (value):
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
        return value.replace (",", "")
    return value

#------------------------------------
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
            # 載入暫存資料
            #print (row[1], row[0])
            info = getFromCache (getCacheFilename (row[0]), {})
            diff = float (getCSVRowNumber(row[10]))
            tmp = {
                # 量能 (從股數->張數)
                "vol" : int(int(getCSVRowNumber(row[2]))/1000),
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
            info[dailyKey] = tmp
            # 做存入的動作
            saveCache (getCacheFilename(stockID), info)
        file.close()

        tmp = {
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

        tmp["pre_price"] = tmp["end_price"] - tmp["diff"]
        # 要補沒有資料的部分
        for stockID, stock in allstock.items():
            if stock.location != "上巿":
                continue
            info = getFromCache (getCacheFilename(stockID), {})
            if dailyKey not in info:
                print (stock.name, stock.id)
                info[dailyKey] = tmp
                # 做存入的動作
                saveCache (getCacheFilename(stockID), info)

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
            info = getFromCache (getCacheFilename (row[0]), {})
            tmp = {
                # 收盤價
                "end_price" : float (getCSVRowNumber(row[2])),
                # 差價
                "diff" : float (getCSVRowNumber(row[3])) if row[3].strip(" ") != "除權" and row[3].strip(" ") != "除息" else None,
                # 開盤價
                "start_price" : float (getCSVRowNumber(row[4])),
                # 最高價
                "high_price" : float (getCSVRowNumber(row[5])),
                # 最低價
                "low_price" : float (getCSVRowNumber(row[6])),
                # 量能 (從股數->張數)
                "vol" : int(int(getCSVRowNumber(row[8]))/1000),
            }
            if tmp["diff"] != None:
                tmp["pre_price"] = tmp["end_price"] - tmp["diff"]
            else:
                tmp["pre_price"] = None
            info[dailyKey] = tmp
            # 做存入的動作
            saveCache (getCacheFilename(stockID), info)
        file.close()

        tmp = {
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

        tmp["pre_price"] = tmp["end_price"] - tmp["diff"]
        # 要補沒有資料的部分
        for stockID, stock in allstock.items():
            if stock.location != "上櫃":
                continue
            info = getFromCache (getCacheFilename(stockID), {})
            if dailyKey not in info:
                print (stock.name, stock.id)
                info[dailyKey] = tmp
                # 做存入的動作
                saveCache (getCacheFilename(stockID), info)

#------------------------------------
# 取得有開盤的日期
print ("=== [取得有開盤的日期] ===")
# 拿台泥來看
info = getFromCache (getCacheFilename ("1101"), {})
dayKeyList = [value for value in info.keys()]
dayKeyList.sort (reverse=True)
file = open ("../info/dailyList.txt", "w", encoding="utf-8")
file.writelines (json.dumps (dayKeyList))
file.close()
print (dayKeyList)

