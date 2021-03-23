# DESC : 轉換文字 -> DB 的中介程式, 把資料存進去DB
# DATE : 2021/3/11
import sys
sys.path.append(r"c:\download\ranb_gametowner\python_module")
from utility import *
from WebViewMgr import WebViewMgr
# 載入這個專案共用模組
sys.path.append (r"..\module")
from AllStockMgr import AllStockMgr
from NetStockInfo import NetStockInfo
from StockDBMgr import StockDBMgr
from cSqlite import cSqlite
import json
import csv

# 取得所有的股票
allstock = AllStockMgr.getAllStock ()

# 更新資料
updateFlag = {
    # 更新基本資料 (己完成)
    "basic":False,
    # 更新 news (己完成)
    "news":False,
    # 更新每日資料 (己完成)
    "daily" : False,
    # 三大法人
    "three" : True,
}

url = "https://tw.stock.yahoo.com/quote/3293/dividend"
print ()
WebViewMgr.loadURL ()
printCountDown (10)

#------------------------------------
# 塞入基本資料
if updateFlag["basic"] == True:
    print ("【更新】個股基本資料")
    basicDB = cSqlite ("../db/basic.db3")
    for stockID, stock in allstock.items():
        print ("=== 處理 %s(%s) ===" % (stock.name, stock.id))
        # 做更新的動作
        basicDB.update ("basic", 
            # 資訊
            {
                # 上巿 / 上櫃
                "location" : stock.location,
                # 股本
                "equity" : stock.getInfoFloat ("股本"),
                # 淨值
                "assetValue" : stock.getInfoFloat ("淨值"),
                # 產業類別
                "business" : stock.getInfo ("產業類別"),
                # 營業比重
                "businessRate" : stock.getInfo ("營業比重"),
            }, 
            # KEY
            {
                # 編號
                "id":int(stockID),
                # 名稱
                "name":stock.name,
            },
        )

    # 整個更新進去
    basicDB.commit()
else:
    print ("【不更新】基本資料")

#------------------------------------
# 塞入基本資料
if updateFlag["news"] == True:
    print ("【更新】新聞")
    newsDB = cSqlite ("../db/news.db3")
    for stockID, stock in allstock.items():
        print ("=== 處理 %s(%s) ===" % (stock.name, stock.id))
        # 取得新聞內容
        newsList = getFromCache ("../info/news_%s.txt" % (stock.id,), [])
        newsList.reverse()
        for index, news in enumerate (newsList):
            date = news["date"].split (" ")[0][1:]
            # 做更新的動作
            newsDB.update ("news", 
                # 資訊
                {
                    "stockID" : int(stockID),
                    "dateStr" : news["date"],
                    "url" : news["url"],
                }, 
                # KEY
                {
                    "title" : news["title"],
                    "date" : date,
                },
            )
        #break

    # 整個更新進去
    newsDB.commit()
else:
    print ("【不更新】新聞")

#------------------------------------
# 更新每日資料
if updateFlag["daily"] == True:
    print ("【更新】每日資料")
    for stockID, stock in allstock.items():
        print ("=== 處理 %s(%s) ===" % (stock.name, stock.id))
        dailyMap = getFromCache ("../info/daily_%s.txt" % (stockID,))
        print ("[count] " + str(len(dailyMap)))
        for dateKey, info in dailyMap.items():
            StockDBMgr.saveDaily (stockID, info)
else:
    print ("【不更新】每日")

#------------------------------------
# 三大法人
if updateFlag["three"] == True:
    print ("【更新】三大法人")
    for stockID, stock in allstock.items():
        print ("=== 處理 %s(%s) ===" % (stock.name, stock.id))
        # single.netInfo["三大法人"]
        for info in single.netInfo["三大法人"]:
            StockDBMgr.saveThree (stockID, info)
        
else:
    print ("【不更新】三大法人")



