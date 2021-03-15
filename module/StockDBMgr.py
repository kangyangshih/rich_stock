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
        # 每日資訊
        self.__DBMap["daily"] = cSqlite ("../db/daily.db3")
        # 基本資料
        self.__DBMap["basic"] = cSqlite ("../db/basic.db3")

    # 解構子    
    def __del__ (self):
        for key, value in self.__DBMap.items():
            value.close()

    def commit (self, dbName):
        self.__DBMap[dbName].commit()
            
    #-----------------------------------------------
    # 新聞相關
    #-----------------------------------------------
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
        newsList = json.loads (rows[0]["newsList"])
        return updateTime, newsList
    
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

    #-----------------------------------------------
    # Daily
    #-----------------------------------------------
    def saveDaily (self, stockID, info, update=False):
        if info["diff"] == None:
            print (stockID, json.dumps(info))
        # # 做程式碼修正
        # if stockID == "8291" and info["diff"] == None:
        #     info["diff"] = 0
        # if stockID == "8936" and info["diff"] == None:
        #     #print ("~~~")
        #     info["diff"] = 0.35
        #     info["pre_price"] = info["end_price"] - info["diff"]
        #     #print (stockID, json.dumps(info))
        # 寫入資料庫
        self.__DBMap["daily"].update ("daily",
            # 資訊
            info,
            # KEY
            {
                "date" : info["date"],
                "id" : int(stockID),
            },
            # 不做更新
            update,
        )
        # 做更新的動作
        self.__DBMap["daily"].commit()
    
    def getDaily (self, stockID):
        # 從資料庫取得新聞
        rows = self.__DBMap["daily"].get (
            # 表單
            "daily", 
            # 取得的欄位
            [
                "date", 
                "end_price", 
                "diff", 
                "start_price", 
                "high_price", 
                "low_price", 
                "vol", 
                "pre_price",
            ],
            # KEY
            {
                "id" : int(stockID),
            },
            # order
            " date desc"
        )
        return rows
    
    # 回傳日期列表
    def getDayKey (self):
        return self.__DBMap["daily"].getFieldList (
            "daily",
            "date",
            # KEY
            {
                "id" : int(stockID),
            },
            # order
            " date desc"
        )
    
StockDBMgr = cStockDBMgr()