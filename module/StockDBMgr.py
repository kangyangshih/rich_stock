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
        self.__DBMap["news"] = cSqlite ("../db/news.db3")
        # 基本資料
        self.__DBMap["basic"] = cSqlite ("../db/basic.db3")

    # 解構子    
    def __del__ (self):
        for key, value in self.__DBMap.items():
            value.close()

    # 取得新聞
    def getNews (self, stockID):
        # 從資料庫取得新聞
        res = self.__DBMap["news"].get (
            # 表單
            "news", 
            # 取得的欄位
            ["id", "date", "dateStr", "title"],
            # KEY
            {
                "stockID" : int(stockID)
            },
            # 排序
            "id desc" 
        )
        return res
    
    # 做新聞的更新
    def saveNews (self, stockID, newsList):
        # 先把新舊資料轉一下
        newsList.reverse()
        # 一筆一筆塞
        for news in newsList:
            # 做更新的動作
            self.__DBMap["news"].update ("news", 
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
                # 不做更新
                False,
            )
            
StockDBMgr = cStockDBMgr()