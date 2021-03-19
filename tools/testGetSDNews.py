# 載入所有 python 共用模組
import sys
sys.path.append(r"c:\download\ranb_gametowner\python_module")
from utility import *
# 載入這個專案共用模組
sys.path.append (r"..\module")
from AllStockMgr import AllStockMgr
from NetStockInfo import NetStockInfo
from StockDBMgr import StockDBMgr
import json
from lxml import etree
import time
from WebViewMgr import WebViewMgr
import random

# 取得所有的股票清單
allstock = AllStockMgr.getAllStock ()
print ("===========")
stockIDList = []
for stockID, stock in allstock.items():
    # 抓取新聞
    updateTime, newsList = StockDBMgr.getNews (stockID)
    #print ("%s news count:%s" % (stock.name, len(newsList)))
    # 檢查資料
    isFound = False
    for news in newsList:
        # 如果檢查到2020 就不做處理
        if news["date"].find ("2020/") != -1:
            break
        # 不是【股利分派】的新聞，就繼續找
        if news["title"].find ("股利分派") != -1:
            #print ("找到股利分配 : " + stock.name)
            stockIDList.append (stockID)
            isFound = True
            break
        if news["title"].find ("擬配息") != -1:
            #print ("找到股利分配 : " + stock.name)
            stockIDList.append (stockID)
            isFound = True
            break

print ("[股利分派] 數量 : "+ str(len(stockIDList)))
stockIDList.sort()
print ("[己有2021配股配息] : " + str(StockDBMgr.get2021SDCount()))

# 一隻一隻去抓取資料
for stockID in stockIDList:
#for stockID, stock in allstock.items():
    # 先檢查資料是不是存在
    if StockDBMgr.checkInfo ("basic", "stockDiv", {"id":int(stockID), "years":"2021"}) == True:
        #print ("%s save, pass" % (stockID,))
        continue
    #if StockDBMgr.checkInfo ("basic", "stockDiv", {"id":int(stockID), "years":"2020"}) == True:
    #    print ("%s 暫時沒有2021，先 Pass" % (stockID,))
    #    continue
    # 開啟網頁
    url = "https://goodinfo.tw/StockInfo/StockDividendPolicy.asp?STOCK_ID=" + str(stockID)
    WebViewMgr.loadURL (url)
    # 取得內容
    xpath = '//*[@id="divDetail"]/table/tbody/tr'
    rowNodes = WebViewMgr.getNodes (xpath)
    print ("[count]", len(rowNodes))
    if len(rowNodes) == 0:
        break
    info = {}
    for rowNode in rowNodes:
        fieldNodes = rowNode.find_elements_by_xpath ('.//td')
        # 只是上下半年的就不處理
        if fieldNodes[0].text.isdigit () == False:
            #print ("[ignore][part]", rowNode.text)
            continue
        # # 沒有EPS就不做處理 (沒有2021 就不會有EPS)
        # if fieldNodes[20].text == "-":
        #     #print ("[ignore][no eps]", rowNode.text)
        #     if fieldNodes[0].text != "-":
        #         print (rowNode.text)
        #     continue
        # 真的還沒有公告。
        if fieldNodes[1].text == "-":
            continue
        #print (rowNode.text)
        # 股利發放年度
        info["years"] = fieldNodes[0].text
        info["money"] = float (fieldNodes[1].text)
        info["moneyHold"] = float(fieldNodes[2].text)
        info["moneyAll"] = float (fieldNodes[3].text)
        info["stock"] = float (fieldNodes[4].text)
        info["stockHold"] = float(fieldNodes[5].text)
        info["stockAll"] = float (fieldNodes[6].text)
        info["sdAll"] = float (fieldNodes[7].text)
        # 如果是 None 就不會寫進去DB。
        if fieldNodes[20].text == "-":
            info["eps"] = None
        else:
            info["eps"] = float(fieldNodes[20].text)
        # 塞進去DB
        StockDBMgr.saveSD (stockID, info, True)
        # 印出來看看
        print ("[%s] %s eps:%s -> %s+%s=%s" % (stockID, 
            info["years"],
            info["eps"],
            info["moneyAll"],
            info["stockAll"],
            info["sdAll"],
        ))
        #break
    #break
    printCountDown (random.randint(15,25))
    # print ("[try sleep]")
    # time.sleep (10)
    # print ("[finish sleep]")
