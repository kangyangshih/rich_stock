# DESC : 暫用的工具，主要是拿來把資料轉存到 sqlite
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
    # 更新 news
    "news":True,
}

#------------------------------------
# 塞入基本資料
if updateFlag["news"] == True:
    print ("【更新】新聞")
    oldDB = cSqlite ("../db/news.db3")
    for stockID, stock in allstock.items():
        print ("=== 處理 %s(%s) ===" % (stock.name, stock.id))
        # 取得新聞內容
        newsList = getFromCache ("../info/news_%s.txt" % (stock.id,), [])
        newsList.reverse()
        for index, news in enumerate (newsList):
            date = news["date"].split (" ")[0][1:]
            # 做更新的動作
            oldDB.update ("news", 
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
    oldDB.commit()
else:
    print ("【不更新】新聞")

