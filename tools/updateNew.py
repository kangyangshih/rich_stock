# 更新新聞
# 注 : 如果可以加上新聞日期更好
import sys
sys.path.append(r"c:\download\ranb_gametowner\python_module")
from utility import *
#WebViewMgr.debugMode ()
# 載入這個專案共用模組
sys.path.append (r"..\module")
from AllStockMgr import AllStockMgr
from WebViewMgr import WebViewMgr
from StockDBMgr import StockDBMgr
import json
import csv
import random

# 取得時間日期 (每天只更新一次新聞)
updateTimeStr = get_hour_str (3)
print ("[updateTimeStr] "+ updateTimeStr)

# 取得所有的股票清單
allstock = AllStockMgr.getAllStock ()

#------------------------------------------------
print ("=== [更新新聞] ===")
# 取得新聞
def getNewsFromYahoo (stockID, pageNum=1):
    # 載入暫存資料
    newsList = []
    #----------------------------------------------
    # 新聞
    newsURLTemplate = "https://tw.stock.yahoo.com/q/h?s=%s&pg=%s"
    for pageIndex in range (pageNum):
        # 取得新聞頁
        url = newsURLTemplate % (stockID, pageIndex+1)
        WebViewMgr.loadURL (url)
        # 取得 xpath
        nodes = WebViewMgr.getNodes ('/html/body/center/table[1]/tbody/tr/td[1]/table[2]/tbody/tr[2]/td/table/tbody/tr[2]/td/table/tbody/tr/td[2]/a')
        timeNodes = WebViewMgr.getNodes ('/html/body/center/table[1]/tbody/tr/td[1]/table[2]/tbody/tr[2]/td/table/tbody/tr[2]/td/table/tbody/tr/td/font')
        print ("[num] " + str(len(nodes)))
        for index, node in enumerate (nodes):
            #print (timeNodes[index].text, node.text)
            #print (node.get_attribute ("href"))
            newsList.append ({
                "title" : node.text,
                "date" : timeNodes[index].text.split (" ")[0][1:],
                "dateStr" : timeNodes[index].text,
                "url" : node.get_attribute ("href"),
            })
    return newsList
stockIDList = [stockID for stockID in allstock.keys()]
random.shuffle (stockIDList)
#for stockID, stock in allstock.items():
for stockID in stockIDList:
    stock = allstock[stockID]
    # 做資料差異更新
    dbUpdateTime, cacheInfo = StockDBMgr.getNews (stockID)
    # 每天只更新一次新聞
    if dbUpdateTime == updateTimeStr:
        print ("%s 己更新" % (stock.name,))
        continue
    print ("=== %s ===" % (stock.name,))
    # 載入暫存資料
    newsList = getNewsFromYahoo (stockID)
    #----------------------------------------------
    #print ("===== cache information =====")
    #for cache in cacheInfo:
    #    print (cache["title"])
    newList = []
    for index in range (len(newsList)):
        found = False
        for cacheIndex in range (len(cacheInfo)):
            if newsList[index]["url"] == cacheInfo[cacheIndex]["url"]:
                found = True
                break
        if found == True:
            print ("found!, index=%s" % (index,))
            newList = newsList[:index]
            break
    if len(newsList) == len(newList):
        print ("[need more news]")
        exit_program ()
    print ("新資料數量:%s" % (len(newList),))
    for cache in newList:
        print (cache["dateStr"], cache["title"])
    # 把資料存起來
    newList.extend (cacheInfo)
    #print ("===== save cache =====")
    #for cache in newList:
    #    print (cache["title"])
    # 做儲存的動作
    StockDBMgr.saveNews (stockID, updateTimeStr, newList)
