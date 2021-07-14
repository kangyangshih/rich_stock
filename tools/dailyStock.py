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
    # 0. 觀注的個股
    0:True,
    # 1. 有設定觀注價格的股票
    1:True,
    # 2. 當日外本比 / 投本比
    2:True,
    # 3. 區間外資、投信的買賣量排行榜
    3:True,
    # 4. 2021 公告後有殖利率的排行榜
    4:True,
    # 5. 過去五天的新聞 (希望可以貼到 notion 去看的)
    5:True,
    # 2021 除權息日
    6:True,
    # 7. 帶量突破5日線
    7:True,
    # 8. 突破近20日高點 / 取得近10日低點
    8:True,
    # 9. 全部股票
    9:True,
}
#--------------------------------------------------
# 0. 觀注的個股
if controlMap[0] == True:
    priorityKey = [
        # 持有的股票
        "持有",
        # 從核心、衛星選出來做操作的股票
        "短期注意",
        # 比較有愛, 比較熟的股票
        "核心", 
        # 比較不熟, 或是偏牛的股票
        "衛星",
        # 股性比較牛
        #"定存",
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
                #break
            if stock.operationType.find (key) != -1:
                value[stockID] = stock
                #break

    # 依照重要性來做處理
    for key in priorityKey:
        file = open("../data/0.觀注個股_%s.txt"%(key,), "w", encoding="utf-8")
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

    file = open ("../data/1.有標價格股票.txt", "w", encoding="utf-8")
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
    file = open ("../data/2.外本比、投本比.txt", "w", encoding="utf-8")
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
    for day in (5, 20, 60):
        file = open ("../data/3.%s外資加投信累計買賣超.txt" % (day,), "w", encoding="utf-8")
        out_total_map, in_total_map, total_total_map = getRangeTotalRate (day)
        printTotalRate (file, "外資+投信累計 %s 日買超排行榜" % (day,), "外資+投信累計 %s 日買超" % (day,), total_total_map, 15)
        file.close()

    # #-----------------------
    # file = open ("../data/3.5外資加投信累計買賣超.txt", "w", encoding="utf-8")
    # for day in (5,):
    #     out_total_map, in_total_map, total_total_map = getRangeTotalRate (day)
    #     printTotalRate (file, "外資+投信累計 %s 日買超排行榜" % (day,), "外資+投信累計 %s 日買超" % (day,), total_total_map, 15)
    # file.close()

    # #-----------------------
    # file = open ("../data/3.20外資加投信累計買賣超.txt", "w", encoding="utf-8")
    # for day in (20,):
    #     out_total_map, in_total_map, total_total_map = getRangeTotalRate (day)
    #     printTotalRate (file, "外資+投信累計 %s 日買超排行榜" % (day,), "外資+投信累計 %s 日買超" % (day,), total_total_map, 15)
    # file.close()

    # #-----------------------
    # file = open ("../data/3.60外資加投信累計買賣超.txt", "w", encoding="utf-8")
    # for day in (60,):
    #     out_total_map, in_total_map, total_total_map = getRangeTotalRate (day)
    #     printTotalRate (file, "外資+投信累計 %s 日買超排行榜" % (day,), "外資+投信累計 %s 日買超" % (day,), total_total_map, 15)
    # file.close()

    #-----------------------
    out_continueMap = {}
    in_continueMap = {}
    for stockID, stock in allstock.items():
        out_counter, in_counter = stock.getContinueBuy (1)
        if out_counter >= 3:
            if out_counter not in out_continueMap:
                out_continueMap[out_counter] = []
            out_continueMap[out_counter].append (stockID)
        if in_counter >= 3:
            if in_counter not in in_continueMap:
                in_continueMap[in_counter] = []
            in_continueMap[in_counter].append (stockID)
    
    #-----------------------
    keyList = [key for key in out_continueMap.keys()]
    keyList.sort (reverse=True)
    file = open ("../data/3.99 外資連買超.txt", "w", encoding="utf-8")
    for key in keyList:
        stockIDList = out_continueMap[key]
        for stockID in stockIDList:
            write (file, "外資連買超 %s 天\n====================\n" % (key,))
            allstock[stockID].dumpInfo (file)
    file.close()

    #-----------------------
    keyList = [key for key in in_continueMap.keys()]
    keyList.sort (reverse=True)
    file = open ("../data/3.99 投信連買超.txt", "w", encoding="utf-8")
    for key in keyList:
        stockIDList = in_continueMap[key]
        for stockID in stockIDList:
            write (file, "投信連買超 %s 天\n====================\n" % (key,))
            allstock[stockID].dumpInfo (file)
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
        # 配太少就暫時不列入
        if stock.now_sd_rate < 3:
            continue
        if stock.now_sd_rate not in tmp:
            tmp[stock.now_sd_rate] = []
        tmp[stock.now_sd_rate].append (stockID) 

    # 做印出的動作
    file = open ("../data/4.2021殖利率排行榜.txt", "w", encoding="utf-8")
    tmpList = changeDict2List (tmp)
    for stockID in tmpList:
        stock = allstock[stockID]
        write (file, "[現在殖利率] %.2f %%", stock.now_sd_rate)
        stock.dumpInfo (file)
    file.close()

#--------------------------------------------------
# 5. 過去五天的新聞 (希望可以貼到 notion 去看的)
def writeNews (file, news):
    file.writelines ("========================\n")
    # 把內容寫下來
    write (file, 
        "* [%s(%s)]( %s ) %s [%s]( %s )", 
        news["name"], 
        news["id"],
        'https://tw.stock.yahoo.com/q/ta?s='+news["id"], 
        news["dateStr"],
        news["title"], 
        news["url"]
    )
    file.writelines ("========================\n")
if controlMap[5] == True:
    # 以日期來做
    newsMap = {}

    nowTimes = time.time()
    keywordList = [
        "列注意股", 
        "稅前每股", 
        "稅前EPS", 
        "發債",
        "庫藏股",
    ]
    for index in range (2):
        # 取得時間字串
        tmpTime = time.gmtime(nowTimes)
        timeStr = "%04d/%02d" % (tmpTime.tm_year, tmpTime.tm_mon - index)
        file = open ("../data/5.新聞_%s.txt" % (timeStr.replace("/", "_"),), "w", encoding="utf-8")
        # 每個股票都去找
        for stockID, stock in allstock.items():
            tmp, newsList = StockDBMgr.getNews (stockID)
            for news in newsList:
                news["id"] = stock.id
                news["name"] = stock.name
                # 日期不對不做處理
                if news["date"].find (timeStr) == -1:
                    continue
                for keyword in keywordList:
                    # 沒有指定字不做處理
                    if news["title"].find (keyword) != -1:
                        if news["date"] not in newsMap:
                            newsMap[news["date"]] = []
                        newsMap[news["date"]].append (news)
        tmpList = changeDict2List (newsMap)
        for news in tmpList:
            writeNews (file, news)
            allstock[news["id"]].dumpInfo(file)
        write (file, "")
        file.close()

#--------------------------------------------------
# 7. 帶量突破5日線, 且均線排好
if controlMap[7] == True:
    # 7.1 帶量突破5日線
    counter = 0
    file = open ("../data/7.1 帶量突破5日線.txt", "w", encoding="utf-8")
    for stockID, stock in allstock.items():
        # 線型要排好 5 > 20 > 60
        if stock.isMASorted () == False:
            continue
        # 取得5日線
        tmp5 = stock.getdayPriceAvg (0, 5)
        # 取得股價
        realtime = stock.getTodayPrice ()
        # 量能要夠, 至少要比5日量大
        vol5 = stock.getdayVolAvg (0, 5)
        vol20 = stock.getdayPriceAvg (0, 20)
        if realtime["vol"] < vol5 * 1.5:
            continue
        if realtime["vol"] < vol20 * 1.2:
            continue
        # 由上往下穿
        if realtime["pre_price"] <= tmp5 and realtime["end_price"] >= tmp5:
            counter += 1
            stock.dumpInfo(file)
    file.close()
    print ("[7.1 帶量突破5日線] ", counter)
    # 7.2 突破後帶量上攻
    counter = 0
    file = open ("../data/7.2 突破後帶量上攻.txt", "w", encoding="utf-8")
    for stockID, stock in allstock.items():
        # 線型要排好 5 > 20 > 60
        if stock.isMASorted () == False:
            continue
        # 取得5日線
        tmp5 = stock.getdayPriceAvg (0, 5)
        pretmp5 = stock.getdayPriceAvg (1, 5)
        # 取得股價
        realtime = stock.getTodayPrice ()
        pretime = stock.getTodayPrice (1)
        # 量能要夠, 至少要比5日量大
        vol5 = stock.getdayVolAvg (0, 5)
        if realtime["vol"] < pretime["vol"]:
            continue
        # 如果小於5日線型, 就不做處理
        if realtime["pre_price"] <= tmp5 or realtime["end_price"] <= tmp5:
            continue
        # 希望是昨天突破5日線，今天補量
        if pretime["pre_price"] <= pretmp5 and pretime["end_price"] >= pretmp5:
            counter += 1
            stock.dumpInfo(file)
    file.close()
    print ("[7.2 突破後帶量上攻] ", counter)

#--------------------------------------------------
# 8. 海龜交易法則
if controlMap[8] == True:
    counter = 0
    file = open ("../data/8. [短期] 海龜交易法則.txt", "w", encoding="utf-8")
    for stockID, stock in allstock.items():
        # 取得今日價
        todayPrice = stock.getTodayPrice ()
        vol5 = stock.getdayVolAvg (0, 5)
        # 量能要比較大
        if todayPrice["vol"] < vol5:
            continue
        # 外資有買進
        out_total5, in_total5 = stock._getThreeTotal (5)
        out_total20, in_total20 = stock._getThreeTotal (20)
        out_total60, in_total60 = stock._getThreeTotal (60)
        if out_total5 < 0 or out_total20 < 0 or out_total60 < 0:
            continue
        # 取得20日高點
        isHigh20 = True
        for index in range (1, 21):
            oldPrice = stock.getTodayPrice (index)
            if todayPrice["high_price"] < oldPrice["high_price"]:
                isHigh20 = False
                break
        if isHigh20 == False:
            continue
        low_price = 10000000
        for index in range (11):
            oldPrice = stock.getTodayPrice (index)
            if oldPrice["low_price"] < low_price:
                low_price = oldPrice["low_price"]
        file.writelines ("%s[%s] 突破近20日高點，近10日低點為 %s\n" % (stock.name, stock.id, low_price))
        stock.dumpInfo (file)
        counter += 1

    file.close()
    print ("total number:", counter)

    counter = 0
    file = open ("../data/8. [長期] 海龜交易法則.txt", "w", encoding="utf-8")
    for stockID, stock in allstock.items():
        # 取得今日價
        todayPrice = stock.getTodayPrice ()
        vol5 = stock.getdayVolAvg (0, 5)
        # 量能要比較大
        if todayPrice["vol"] < vol5:
            continue
        # 外資有買進
        out_total5, in_total5 = stock._getThreeTotal (5)
        out_total20, in_total20 = stock._getThreeTotal (20)
        out_total60, in_total60 = stock._getThreeTotal (60)
        if out_total5 < 0 or out_total20 < 0 or out_total60 < 0:
            continue
        if in_total5 < 0 or in_total20 < 0 or in_total60 < 0:
            continue
        # 取得55日高點
        isHigh20 = True
        for index in range (1, 56):
            oldPrice = stock.getTodayPrice (index)
            if todayPrice["high_price"] < oldPrice["high_price"]:
                isHigh20 = False
                break
        if isHigh20 == False:
            continue
        low_price = 10000000
        for index in range (21):
            oldPrice = stock.getTodayPrice (index)
            if oldPrice["low_price"] < low_price:
                low_price = oldPrice["low_price"]
        file.writelines ("%s[%s] 突破近55日高點，近20日低點為 %s\n" % (stock.name, stock.id, low_price))
        stock.dumpInfo (file)
        counter += 1

    file.close()
    print ("total number:", counter)


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

