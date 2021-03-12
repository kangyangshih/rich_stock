# DESC : 用來取得資料庫
# DATE : 2021/3/12

import sys
sys.path.append(r"c:\download\ranb_gametowner\python_module")
from utility import *
from excel_utility import *
import json
sys.path.append (r"..\module")
from cSqlite import cSqlite

class cStockDBMgr:

    # 資料庫的對應表
    __DBMap = {}

    # 建構子
    def __init__(self):
        # 新聞
        #self.__DBMap["news"] = cSqlite ("../db/news.db3")
        # 基本資料
        self.__DBMap["basic"] = cSqlite ("../db/basic.db3")

    # 解構子    
    def __del__ (self):
        for key, value in self.__DBMap.items():
            value.close()

    # 取得新聞
    def getNews (self, stockID):
        # 從資料庫取得新聞
        rows = self.__DBMap["basic"].get (
            # 表單
            "news", 
            # 取得的欄位
            ["updateTime", "newsList"],
            # KEY
            {
                "id" : int(stockID)
            },
        )
        # 串成想要的資料
        updateTime = rows[0]["updateTime"]
        newsList = json.loads (rows[0]["newList"])
        return updateTimeStr, newsList
    
    # 做新聞的更新
    def saveNews (self, stockID, updateTime, newsList):
        #print (json.dumps (newsList))
        # 做更新的動作
        self.__DBMap["basic"].update ("news",
            # 資訊
            {
                "updateTime" : updateTime,
                "newsList" : json.dumps (newsList),
            },
            # KEY
            {
                "id" : int(stockID),
            },
        )
        # 做更新的動作
        self.__DBMap["basic"].commit()
        # 結束
        return

            
StockDBMgr = cStockDBMgr()