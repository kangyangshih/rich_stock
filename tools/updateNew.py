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

def getNewsFilename (stockID):
    return "../info/news_%s.txt" % (stockID,)

# 取得所有的股票清單
allstock = AllStockMgr.getAllStock ()

# 取得時間日期 (每天只更新一次新聞)
updateTimeStr = get_day_str ()
stockUpdateTimeMap = getFromCache ("../info/newsUpdateTime.txt", {})

#------------------------------------------------
print ("=== [更新新聞] ===")
for stockID, stock in allstock.items():
    # 每天只更新一次新聞
    if stockID in stockUpdateTimeMap and stockUpdateTimeMap[stockID] == updateTimeStr:
        print ("%s 今日己更新，不再更新" % (stock.name,))
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
        print (timeNodes[index].text, node.text)
        #print (node.get_attribute ("href"))
        info.append ({
            "title" : node.text,
            "date" : timeNodes[index].text,
            "url" : node.get_attribute ("href"),
        })
    #----------------------------------------------
    # 載入第二頁
    # https://tw.stock.yahoo.com/q/h?s=1101&pg=2
    # 載入第一頁
    url = url+"&pg=2"
    WebViewMgr.loadURL (url)
    # 取得 xpath
    nodes = WebViewMgr.getNodes ('/html/body/center/table[1]/tbody/tr/td[1]/table[2]/tbody/tr[2]/td/table/tbody/tr[2]/td/table/tbody/tr/td[2]/a')
    timeNodes = WebViewMgr.getNodes ('/html/body/center/table[1]/tbody/tr/td[1]/table[2]/tbody/tr[2]/td/table/tbody/tr[2]/td/table/tbody/tr/td/font')
    for index, node in enumerate (nodes):
        print (timeNodes[index].text, node.text)
        #print (node.get_attribute ("href"))
        info.append ({
            "title" : node.text,
            "date" : timeNodes[index].text,
            "url" : node.get_attribute ("href"),
        })
    
    #----------------------------------------------
    # 把資料存起來
    saveCache (getNewsFilename(stockID), info)
    stockUpdateTimeMap[stockID] = updateTimeStr
    saveCache ("../info/newsUpdateTime.txt", stockUpdateTimeMap)
    #break
