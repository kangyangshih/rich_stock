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
import json
import csv

# 取得時間日期 (每天只更新一次新聞)
updateTimeStr = get_hour_str ()

# 加入這次更新的新聞
g_updateNews = getFromCache ("../cache_news_%s.txt" % (updateTimeStr,), [])
def addUpdateNews (news):
    # 加入
    g_updateNews.append (news)
    # 寫成檔案
    tmpfile = open ("../update_%s.txt" % (updateTimeStr,), "w", encoding="utf-8")
    for news in g_updateNews:
        tmpfile.writelines ("* %s [%s](%s)<br/>\n" % (news["date"],
                news["title"], 
                news["url"]
            )
        )
    tmpfile.close()
    # 暫存起來
    saveCache ("../cache_news_%s.txt" % (updateTimeStr,), g_updateNews)

# 取得新聞的檔案名稱
def getNewsFilename (stockID):
    return "../info/news_%s.txt" % (stockID,)

# 取得所有的股票清單
allstock = AllStockMgr.getAllStock ()

stockUpdateTimeMap = getFromCache ("../info/newsUpdateTime.txt", {})

#------------------------------------------------
print ("=== [更新新聞] ===")
for stockID, stock in allstock.items():
    # 每天只更新一次新聞
    if stockID in stockUpdateTimeMap and stockUpdateTimeMap[stockID] == updateTimeStr:
        print ("%s 最多每小時更新一次。不再更新" % (stock.name,))
        continue
    # 載入暫存資料
    info = []
    #----------------------------------------------
    # 載入第一頁
    url = "https://tw.stock.yahoo.com/q/h?s=" + stockID
    WebViewMgr.loadURL (url)
    print ("=== %s ===" % (stock.name,))
    # 取得 xpath
    nodes = WebViewMgr.getNodes ('/html/body/center/table[1]/tbody/tr/td[1]/table[2]/tbody/tr[2]/td/table/tbody/tr[2]/td/table/tbody/tr/td[2]/a')
    timeNodes = WebViewMgr.getNodes ('/html/body/center/table[1]/tbody/tr/td[1]/table[2]/tbody/tr[2]/td/table/tbody/tr[2]/td/table/tbody/tr/td/font')
    for index, node in enumerate (nodes):
        #print (timeNodes[index].text, node.text)
        #print (node.get_attribute ("href"))
        info.append ({
            "title" : node.text,
            "date" : timeNodes[index].text,
            "url" : node.get_attribute ("href"),
        })
    #----------------------------------------------
    # 做資料差異更新
    cacheInfo = getFromCache (getNewsFilename(stockID), [])
    #print ("===== cache information =====")
    #for cache in cacheInfo:
    #    print (cache["title"])
    newList = []
    for index in range (len(info)):
        found = False
        for cacheIndex in range (len(cacheInfo)):
            if info[index]["url"] == cacheInfo[cacheIndex]["url"]:
                found = True
                break
        if found == True:
            print ("found!, index=%s" % (index,))
            newList = info[:index]
            break
    print ("新資料數量:%s" % (len(newList),))
    for cache in newList:
        print (cache["date"], cache["title"])
        addUpdateNews (cache)
    newList.extend (cacheInfo)
    #print ("===== save cache =====")
    #for cache in newList:
    #    print (cache["title"])
    #----------------------------------------------
    # 把資料存起來
    saveCache (getNewsFilename(stockID), newList)
    stockUpdateTimeMap[stockID] = updateTimeStr
    saveCache ("../info/newsUpdateTime.txt", stockUpdateTimeMap)
    #break
