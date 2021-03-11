# 載入所有 python 共用模組
import sys
sys.path.append(r"c:\download\ranb_gametowner\python_module")
from utility import *
# 載入這個專案共用模組
sys.path.append (r"..\module")
from AllStockMgr import AllStockMgr
from NetStockInfo import NetStockInfo
import json
from lxml import etree
import time
from WebViewMgr import WebViewMgr

# 取得新聞
def getNews (stockID):
    filename = "../info/news_%s.txt" % (stockID,)
    return getFromCache (filename, [])

# 取得所有的股票清單
allstock = AllStockMgr.getAllStock ()
print ("===========")
stockIDList = []
for stockID, stock in allstock.items():
    # 抓取新聞
    newsList = getNews (stockID)
    #print ("%s news count:%s" % (stock.name, len(newsList)))
    # 檢查資料
    isFound = False
    for news in newsList:
        # 如果檢查到2020 就不做處理
        if news["date"].find ("2020/") != -1:
            break
        # 不是【股利分派】的新聞，就繼續找
        if news["title"].find ("股利分派") == -1:
            continue
        print ("找到股利分配 : " + stock.name)
        stockIDList.append (stockID)
        isFound = True
        break
print ("[股利分派] 數量 : "+ str(len(stockIDList)))
#stockIDList = stockIDList[:1]
cacheMap = getFromCache ("../cacheSD.txt", {})
print ("[己抓取] 數量 : " + str(len(cacheMap)))
for stockID in stockIDList:
    stock = allstock[stockID]
    if stockID in cacheMap:
        continue
    print ("[處理] %s(%s)" % (stock.name, stock.id))
    #--------------------------------
    # 更新【股利分配】
    # https://tw.stock.yahoo.com/d/s/dividend_1236.html
    url = 'https://tw.stock.yahoo.com/d/s/dividend_%s.html' % (stockID,)
    WebViewMgr.loadURL (url)
    xpath = '/html/body/table[1]/tbody/tr/td/table[2]/tbody/tr'
    rowNodes = WebViewMgr.getNodes (xpath)
    rowNodes = rowNodes[1:]
    res = []
    for rowNode in rowNodes:
        nodes = rowNode.find_elements_by_xpath ('.//td')
        #for node in nodes:
        #    print (node.text)
        tmp = {}
        tmp["獲利年度"] = str(int(nodes[0].text[:3]) + 1911) + nodes[0].text[3:]
        tmp["現金股利發放日"] = nodes[1].text
        tmp["現金股利"] = float(nodes[2].text)
        tmp["盈餘配股"] = float(nodes[3].text)
        tmp["公積配股"] = float(nodes[4].text)
        tmp["股票股利"] = float(nodes[5].text)
        tmp["合計"] = float(nodes[6].text)
        res.append (tmp)
    #print (json.dumps (res))
    if res[0]["獲利年度"] == "2020年":
        print ("==========")
        print ("[有配息資料] %s %s %s" % (res[0]["獲利年度"], res[0]["現金股利"], res[0]["合計"]))
        cacheMap[stockID] = res
        saveCache ("../cacheSD.txt", cacheMap)

    # 載入暫存資料
    #info = getFromCache ("../info/%s.txt" % (stockID,), {})
    #--------------------------------
    # 更新【季 EPS】 
    # 【季EPS】2020Q4 EPS:0.14
    # tmpList = changeDict2List (stock.netInfo["QEPS"])
    # for index in range (100):
    #     quarterly = tmpList[index]["年度"]
    #     if quarterly.find ("Q") == -1:
    #         continue
    #     print ("【季EPS】%s EPS:%s" % (
    #             quarterly,
    #             stock.getInfo ("QEPS", quarterly, "EPS"),
    #         )
    #     )
    #     break

    #--------------------------------
    # 更新【股利分配】

    # 【股利分配】 2019 0.15 0 0.3
    # print ("【股利分配】", 
    #     info["配股配息"][0]["所屬年度"], 
    #     info["配股配息"][0]["EPS"], 
    #     info["配股配息"][0]["股票股利"], 
    #     info["配股配息"][0]["現金股利"],
    # )

    # 取得配息資料
    # 更新資料 (試著更新一下)
    # if info["配股配息"][0]["所屬年度"] == "2019":
    #     res, tmp = NetStockInfo.getHistockStockDivide (stockID)
    #     if res == False:
    #         continue
    #     info["配股配息"] = tmp
    #     if len(info["配股配息"]) > 0:
    #         print ("配股配息", json.dumps(info["配股配息"][0]))
    #     if info["配股配息"][0]["所屬年度"] != "2019":
    #         # 把資料存起來
    #         saveCache ("../info/%s.txt" % (stockID,), info)
