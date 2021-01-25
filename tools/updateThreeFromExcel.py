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
    return "../info/%s.txt" % (stockID,)

allstock = AllStockMgr.getAllStock ()

# 取得內容
def getCSVRowNumber (value):
    if value == "":
        return "0"
    if value == "0":
        return "0"
    if value.find (",") == -1:
        return "0"
    return value[:-4]

# 先取得 ../tmp 下的 csv 檔案
filelist = get_dir_file_list ("../threeDaily")
for filename in filelist:

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
            info = getFromCache (getCacheFilename (row[0]), {})
            if "三大法人" not in info:
                info["三大法人"] = {}
            #print ("~~ %s (%s) ~~~" % (allstock[stockID].name, stockID))
            #print (row)
            #print (row[10][:-4], row[13][:-4], row[16][:-4], row[19][:-4], row[23][:-4])
            tmp = {
                # 日期
                "date" : threeKey,
                # 外資
                "out_buy" : getCSVRowNumber(row[8]),
                "out_sell" : getCSVRowNumber(row[9]),
                "out" : getCSVRowNumber(row[10]),
                # 投信
                "in_buy" : getCSVRowNumber(row[11]),
                "in_sell" : getCSVRowNumber(row[12]),
                "in" : getCSVRowNumber(row[13]),
                # 自營商(自行買賣)
                "self_0_buy" : getCSVRowNumber(row[14]),
                "self_0_sell" : getCSVRowNumber(row[15]),
                "self_0" : getCSVRowNumber(row[16]),
                # 自營商(避險)
                "self_1_buy" : getCSVRowNumber(row[17]),
                "self_1_sell" : getCSVRowNumber(row[18]),
                "self_1" : getCSVRowNumber(row[19]),
                # 總計
                "total" : getCSVRowNumber(row[23]),
            }
            #print (tmp)
            info["三大法人"][threeKey] = tmp
            # 做存入的動作
            saveCache (getCacheFilename(stockID), info)
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
            info = getFromCache (getCacheFilename(stockID), {})
            if "三大法人" not in  info:
                info["三大法人"] = {}
            if threeKey not in info["三大法人"]:
                #print ("%s 在 %s 沒有三大法人資料，補空的進去" % (stock.name, threeKey))
                info["三大法人"][threeKey] = tmp
                saveCache (getCacheFilename(stockID), info)

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
        print ("上巿檔案, 日期:", threeKey)
        file = open (filename, "r", encoding="utf-8")
        rows = csv.reader(file, delimiter=',', quotechar='"')
        for row in rows:
            if len(row) == 0:
                continue
            stockID = row[0]
            if row[0] not in allstock:
                continue
            # 載入暫存資料
            info = getFromCache (getCacheFilename(row[0]), {})
            if "三大法人" not in info:
                info["三大法人"] = {}
            #print ("~~ %s (%s) ~~~" % (allstock[stockID].name, stockID))
            #print (row)
            #print (row[10][:-4], row[13][:-4], row[16][:-4], row[19][:-4], row[23][:-4])
            tmp = {
                # 日期
                "date" : threeKey,
                # 外資
                "out_buy" : getCSVRowNumber(row[2]),
                "out_sell" : getCSVRowNumber(row[3]),
                "out" : getCSVRowNumber(row[4]),
                # 投信
                "in_buy" : getCSVRowNumber(row[8]),
                "in_sell" : getCSVRowNumber(row[9]),
                "in" : getCSVRowNumber(row[10]),
                # 自營商(自行買賣)
                "self_0_buy" : getCSVRowNumber(row[12]),
                "self_0_sell" : getCSVRowNumber(row[13]),
                "self_0" : getCSVRowNumber(row[14]),
                # 自營商(避險)
                "self_1_buy" : getCSVRowNumber(row[15]),
                "self_1_sell" : getCSVRowNumber(row[16]),
                "self_1" : getCSVRowNumber(row[17]),
                # 總計
                "total" : getCSVRowNumber(row[18]),
            }
            #print (tmp)
            info["三大法人"][threeKey] = tmp
            # 做存入的動作
            saveCache (getCacheFilename(stockID), info)
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
            info = getFromCache (getCacheFilename(stockID), {})
            if "三大法人" not in  info:
                info["三大法人"] = {}
            if threeKey not in info["三大法人"]:
                #print ("%s 在 %s 沒有三大法人資料，補空的進去" % (stock.name, threeKey))
                info["三大法人"][threeKey] = tmp
                saveCache (getCacheFilename(stockID), info)
































