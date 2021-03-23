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
    # daily / news / basic / three
    __DBMap = {}

    # 建構子
    def __init__(self):
        # 每日資訊
        #self.__DBMap["daily"] = cSqlite ("../db/daily.db3")
        # 新聞
        #self.__DBMap["news"] = cSqlite ("../db/news.db3")
        # 基本資料
        #self.__DBMap["basic"] = cSqlite ("../db/basic.db3")
        pass
    
    def getDB (self, key):
        # 如果有載入就做處理
        if key not in self.__DBMap:
            self.__DBMap[key] = cSqlite ("../db/%s.db3" % (key,))
        return self.__DBMap[key]

    # 解構子    
    def __del__ (self):
        for key, value in self.__DBMap.items():
            print ("%s closed " % (key,))
            value.close()

    def commit (self, dbName):
        self.getDB(dbName).commit()
    
    # 檢查資料是不是有存在
    def checkInfo (self, dbName, tableName, keyMap):
        #return self.__DBMap[dbName].checkInfo (tableName, keyMap, False)
        return self.getDB(dbName).checkInfo (tableName, keyMap, False)
        
    #-----------------------------------------------
    # 三大法人
    #-----------------------------------------------
    # 儲存三大法人
    def saveThree (self, stockID, info):
        pass

    # 取得三大法人
    def getThree (self, stockID):
        pass
    
    #-----------------------------------------------
    # 新聞相關
    #-----------------------------------------------
    # 取得新聞
    def getNews (self, stockID):
        # 從資料庫取得新聞
        rows = self.getDB("news").get (
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
        self.getDB("news").update ("news",
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
        self.getDB("news").commit()
    
    #-----------------------------------------------
    # 配股配息
    #-----------------------------------------------
    # 記錄配股配息
    def saveSD (self, stockID, info, update=False):
        self.getDB("basic").update ("stockDiv",
            info,
            {
                "id" : int(stockID),
                "years" : info["years"],
            },
        )
        self.getDB("basic").commit()
    
    # 取得配股配息
    def getSD (self, stockID):
        return self.getDB("basic").get ("stockDiv",
            # 想要的欄位
            [
                "years", "moneyAll", "stockAll", "sdAll", "eps",
            ],
            # 條件
            {
                "id" : int(stockID),
            },
            # ORDER BY
            "years desc"
        )
    
    def get2021SDCount (self):
        return int(self.getDB("basic").selectCommand ("select count(*) from stockDiv where years='2021'")[0][0])

    #-----------------------------------------------
    # Daily
    #-----------------------------------------------
    def saveDaily (self, stockID, info, update=False):
        # 寫入資料庫
        self.getDB("daily").update ("daily",
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
        self.getDB("daily").commit()
    
    def getDaily (self, stockID):
        # 從資料庫取得新聞
        rows = self.getDB("daily").get (
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
        return self.getDB("daily").getFieldList (
            "daily",
            "date",
            # KEY
            {
                "id" : 1101,
            },
            # order
            " date desc"
        )
    
StockDBMgr = cStockDBMgr()