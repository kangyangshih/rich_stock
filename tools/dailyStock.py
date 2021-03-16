# DESC : 每天的股票日報
# DATE : 2021/2/26

import sys
sys.path.append(r"c:\download\ranb_gametowner\python_module")
from utility import *
sys.path.append (r"..\module")
from AllStockMgr import AllStockMgr
from NetStockInfo import NetStockInfo
from StockDBMgr import StockDBMgr
import json
import time

#--------------------------------------------------
# 使用的 API

# 做寫檔的動作
def write (file, strFormat, *args):
    strtmp = (strFormat+"\n") % args
    print (strtmp, end="")
    file.writelines (strtmp)

# 做輸出的動作
def printTotalRate (file, title, header, tmpMap, num=15):
    write (file, "#-------------------------------")
    write (file, title)
    write (file, "#-------------------------------")
    stockIDList = changeDict2List (tmpMap)
    stockIDList = stockIDList[:num]
    for stockID in stockIDList:
        write (file, "%s : %.4f" % ( header, getKeyByValue(tmpMap, stockID)))
        allstock[stockID].dumpInfo(file)

# 取得所有的股票
allstock = AllStockMgr.getAllStock ()
# 輸出控制
controlMap = {
    0:True,
    1:True,
    2:True,
    3:True,
    4:True,
    5:True,
    6:True,
    7:True,
    8:True,
    9:True,
}
#--------------------------------------------------
# 0. 觀注的個股
if controlMap[0] == True:
    priorityKey = [
        "持有",
        "短期注意",
        "核心", 
        "衛星",
    ]

    stockOrder = {}
    for key in priorityKey:
        stockOrder[key] = {}

    for stockID, stock in allstock.items():
        # 特別處理持有型股票
        if stock.holdPrice != 0:
            stockOrder["持有"][stockID] = stock
        # 如果有在裏面, 就依照順序
        for key, value in stockOrder.items():
            # 換個判定寫法
            if stock.future.find (key) != -1:
                value[stockID] = stock
                break
            if stock.operationType.find (key) != -1:
                value[stockID] = stock
                break

    file = open("../0.觀注個股.txt", "w", encoding="utf-8")
    # 依照重要性來做處理
    for key in priorityKey:
        write (file, "#-------------------------------")
        write (file, "# %s", key)
        write (file, "#-------------------------------")
        # 一隻一隻去抓資料處理
        for stockID, stock in stockOrder[key].items():
            # 把資料 dump 下來
            stock.dumpInfo (file)
            # 暫時只先抓一隻
            #break
        # 暫時只抓持有的
        #break
    file.close()

#--------------------------------------------------
# 1. 有設定觀注價格的股票
if controlMap[1] == True:
    modify_list = []
    for stockID, stock in allstock.items():
        if stock.holdPrice != 0:
            modify_list.append (stockID)
            continue
        if stock.buyPrice != 0:
            modify_list.append (stockID)
            continue
        if stock.emptyPrice != 0:
            modify_list.append (stockID)
            continue

    file = open ("../1.有標價格股票.txt", "w", encoding="utf-8")
    for stockID in modify_list:
        allstock[stockID].dumpInfo (file)
    file.close()


#--------------------------------------------------
# 2. 外本比 / 投本比

# 取得今天的外本比、投本比前 10 名
def getInOutRate ():
    out_map = {}
    in_map = {}
    all_map = {}
    for stockID, stock in allstock.items():
        out_total, in_total = stock._getThreeTotal (1)
        out_total_rate = stock._getBuyRate (out_total)
        if out_total_rate >= 0.001:
            if out_total_rate not in out_map:
                out_map[out_total_rate] = []
            out_map[out_total_rate].append (stockID)
        in_total_rate = stock._getBuyRate (in_total)
        if in_total_rate >= 0.001:
            if in_total_rate not in in_map:
                in_map[in_total_rate] = []
            in_map[in_total_rate].append (stockID)
        all_total_rate = stock._getBuyRate (out_total + in_total)
        if all_total_rate >= 0.001:
            if all_total_rate not in all_map:
                all_map[all_total_rate] = []
            all_map[all_total_rate].append (stockID)
    return out_map, in_map, all_map

if controlMap[2] == True:
    # 數量
    num = 10
    file = open ("../2.外本比、投本比.txt", "w", encoding="utf-8")
    out_map, in_map, all_map = getInOutRate ()
    printTotalRate (file, "投信今日買超排行榜", "投信買超", in_map, num)
    printTotalRate (file, "外資今日買超排行榜", "外資買超", out_map, num)
    printTotalRate (file, "外資+投信今日買超排行榜", "外資+投信買超", all_map, num)
    file.close()

#--------------------------------------------------
# 3. 區間外資、投信的買賣量排行榜
def getRangeTotalRate (day):
    out_total_map = {}
    in_total_map = {}
    total_total_map = {}
    for stockID, stock in allstock.items():
        # 取得 5 日累積
        out_total, in_total = stock._getThreeTotal (day)
        # 取得 5 日的外本比
        out_total_rate = stock._getBuyRate (out_total)
        if out_total_rate > 0.01:
            if out_total_rate not in out_total_map:
                out_total_map[out_total_rate] = []
            out_total_map[out_total_rate].append (stockID)
        # 取得 5 日的投本比
        in_total_rate = stock._getBuyRate (in_total)
        if in_total_rate > 0.01:
            if in_total_rate not in in_total_map:
                in_total_map[in_total_rate] = []
            in_total_map[in_total_rate].append (stockID)
        # 取得 5 日的總合比
        all_total_rate = stock._getBuyRate (out_total + in_total)
        if all_total_rate > 0.01:
            if all_total_rate not in total_total_map:
                total_total_map[all_total_rate] = []
            total_total_map[all_total_rate].append (stockID)
    return out_total_map, in_total_map, total_total_map

if controlMap[3] == True:
    file = open ("../3.外資加投信累計買賣超.txt", "w", encoding="utf-8")
    for day in (5, 30):
        out_total_map, in_total_map, total_total_map = getRangeTotalRate (day)
        printTotalRate (file, "外資+投信累計 %s 日買超排行榜" % (day,), "外資+投信累計 %s 日買超" % (day,), total_total_map, 15)
    file.close()

#--------------------------------------------------
# 4. 2021 公告後有殖利率的排行榜
if controlMap[4] == True:
    tmp = {}
    for stockID, stock in allstock.items():
        # 還沒有公告就不做處理
        if stock.sd2021 == None:
            continue
        # 取得收盤價
        realtime = stock.getTodayPrice ()
        # 暫時借塞
        stock.now_sd_rate = (stock.sd2021 / realtime["end_price"] * 100) + stock.sd2021_stock * 10
        if stock.now_sd_rate not in tmp:
            tmp[stock.now_sd_rate] = []
        tmp[stock.now_sd_rate].append (stockID) 

    # 做印出的動作
    file = open ("../4.2021殖利率排行榜.txt", "w", encoding="utf-8")
    tmpList = changeDict2List (tmp)
    for stockID in tmpList:
        stock = allstock[stockID]
        write (file, "[現在殖利率] %.2f %%", stock.now_sd_rate)
        stock.dumpInfo (file)
    file.close()

#--------------------------------------------------
# 5. 過去五天的新聞 (希望可以貼到 notion 去看的)
if controlMap[5] == True:
    def writeNews (file, stock, news):
        # 把內容寫下來
        write (file, 
            "* [%s(%s)](%s) %s [%s](%s)<br/>", 
            stock.name, 
            stock.id,
            'https://tw.stock.yahoo.com/q/ta?s='+stock.id, 
            news["dateStr"],
            news["title"], 
            news["url"]
        )

    nowTimes = time.time()
    for index in range (2):
        # 取得時間字串
        tmpTime = time.gmtime(nowTimes)
        timeStr = "%04d/%02d" % (tmpTime.tm_year, tmpTime.tm_mon - index)
        file = open ("../5.新聞_%s.txt" % (timeStr.replace("/", "_"),), "w", encoding="utf-8")
        # 每個股票都去找
        for stockID, stock in allstock.items():
            tmp, newsList = StockDBMgr.getNews (stockID)
            for news in newsList:
                # 日期不對不做處理
                if news["date"].find (timeStr) == -1:
                    continue
                # 沒有指定字不做處理
                if news["title"].find ("列注意股") != -1:
                    writeNews (file, stock, news)
                    continue
                if news["title"].find ("稅前每股") != -1:
                    writeNews (file, stock, news)
                    continue
                if news["title"].find ("稅前EPS") != -1:
                    writeNews (file, stock, news)
                    continue
        write (file, "")
        file.close()

#--------------------------------------------------
# 6. 在布林通道上緣的股票
if controlMap[6] == True:
    list6 = []
    list7 = []
    for stockID, stock in allstock.items():
        # 取得股價
        realtime = stock.getTodayPrice ()
        # 取得布林通道
        bband_up, bband, bband_down, msg = stock.getBBand ()
        # 如果在上緣就做記錄下來
        if realtime["end_price"] > bband_up * 0.995:
            list6.append (stockID)
        if realtime["end_price"] < bband_down * 1.005:
            list7.append (stockID)

    file = open ("../6.bbandUp.txt", "w", encoding="utf-8")
    for stockID in list6:
        allstock[stockID].dumpInfo (file)
    file.close()

    # 7. 在布林通道下緣
    file = open ("../7.bbandDown.txt", "w", encoding="utf-8")
    for stockID in list7:
        allstock[stockID].dumpInfo (file)
    file.close()

#--------------------------------------------------
# 9. 所有的股票
if controlMap[9] == True:
    file = open ("../9.所有股票.txt", "w", encoding="utf-8")
    # 依照重要性來做處理
    # 一隻一隻去抓資料處理
    for stockID, stock in allstock.items():
        # 把資料 dump 下來
        stock.dumpInfo (file)
        # 暫時只先抓一隻
        #break
    file.close()

