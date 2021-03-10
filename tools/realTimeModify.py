# 做及時的報價, 目前每一分鐘一次
# DESC : 2020/11/2

# Todo

#---------------------------
# 載入所有 python 共用模組
#---------------------------
import sys
sys.path.append(r"c:\download\ranb_gametowner\python_module")
from utility import *
# 載入這個專案共用模組
sys.path.append (r"..\module")
from AllStockMgr import AllStockMgr
from NetStockInfo import NetStockInfo
import json

# 取得所有的股票
allstock = AllStockMgr.getAllStock ()
priorityKey = [
    "持有",
    "權重股",
    "短期注意",
    "做多",
]

stockOrder = {}
for key in priorityKey:
    stockOrder[key] = {}

# 取得移除的
removeCache = "../today_remove_%s.json" % (get_day_str(),)
g_removeList = getFromCache (removeCache, [])
print (g_removeList)

# 把想要監控的做一下分類
for stockID, stock in allstock.items():
    if stockID in g_removeList:
        continue
    if stock.holdPrice != 0:
        stockOrder["持有"][stockID] = stock
        continue
    if stock.future.find ("權重股") != -1:
        stockOrder["權重股"][stockID] =  stock
        continue
    if stock.future.find ("短期注意") != -1:
        stockOrder["短期注意"][stockID] =  stock
        continue
    if stock.buyPrice != 0:
        stockOrder["做多"][stockID] = stock
        continue

# 印出來結果
def printRealtimeStock (stockType, stock, removeList, realtime, isPrint=True):
    #------------------------------
    if stockType == "持有":
        #print (stock.holdPrice, type(stock.holdPrice))
        # 鈊象(3293) 770(750) -3.0 4,950 
        command = "%s(%s) %s(%s) %.1f %.1f%% 量:%s" % (
            stock.name, 
            stock.id, 
            realtime["now_price"], 
            stock.holdPrice,
            realtime["now_result"], 
            realtime["now_result_rate"],
            realtime["now_vol"],
        )
        if isPrint == True:
            print (command)
        return command

    #------------------------------
    if stockType == "權重股":
        # 計算影響到大盤多少
        pointToAll = realtime["now_result"] * stock.pointToAll
        command = "%s(%s) %s %.1f(大盤:%.2f) %1.f%% 量:%s" % (
            stock.name, 
            stock.id, 
            realtime["now_price"], 
            realtime["now_result"], 
            pointToAll,
            realtime["now_result_rate"],
            realtime["now_vol"],
        )
        if isPrint == True:
            print (command)
        return command

    #------------------------------
    if stockType == "短期注意":
        if stock.buyPrice == 0:
            command = "%s(%s) %s %.1f %.1f%% 量:%s" % (
                stock.name, 
                stock.id, 
                realtime["now_price"], 
                realtime["now_result"], 
                realtime["now_result_rate"],
                realtime["now_vol"],
            )
            if isPrint == True:
                print (command)
        else:
            command = "%s(%s) %s(%s) %.1f %.1f%% 量:%s" % (
                stock.name, 
                stock.id, 
                realtime["now_price"], 
                stock.buyPrice,
                realtime["now_result"], 
                realtime["now_result_rate"],
                realtime["now_vol"],
            )
            if isPrint == True:
                print (command)
        return command

    #------------------------------
    # 做多的，以盡量靠近為主
    if stockType == "做多":
        #print ("=========")
        #print ("%s %s %s %s" % (stock.name, stock.id, realtime["now_price"], stock.buyPrice))
        # 如果差太遠就先不理他
        if float(realtime["pre_date_price"]) * 0.9 > stock.buyPrice:
            print ("%s(%s) 現價(%s)和買價(%s)差太遠, 不列入及時" % (stock.name, stock.id, realtime["pre_date_price"], stock.buyPrice))
            if stockID not in removeList:
                removeList.append (stockID)
            return
        command = "%s(%s) %s(%s) %.1f %.1f%% %s" % (
            stock.name, 
            stock.id, 
            realtime["now_price"], 
            stock.buyPrice,
            realtime["now_result"], 
            realtime["now_result_rate"],
            realtime["now_vol"],
        )
        if isPrint == True:
            print (command)
        return command

#------------------------------
# 做一個定時更新的動作
while True:
    # 先清除畫面
    clear_console ()
    # 抓取想要更新的股票
    for stockType, stockMap in stockOrder.items():
        print ("=======%s=======" % (stockType,))
        # 可買入清單
        buyList = []
        # 在布林通道上緣
        bup = []
        # 今天突破上緣
        bupstart = []
        # 在布林通道下緣
        bdown = []
        # 今天跌破下緣
        bdownstart = []
        # 依照跌幅來做處理
        tmpDict = {}
        for stockID, stock in stockMap.items():
            # 取得及時資訊
            #print (stock.id, stock.name)
            realtime = None
            try:
                realtime = NetStockInfo.getYahooRealtime (stock.id, realtime=True)
            except:
                continue
            # 要分區做顯示
            if stockType == "做多" or stockType == "短期注意":
                # 如果差太多就不做處理
                tmp = printRealtimeStock (stockType, stock, g_removeList, realtime, False)
                if tmp == None:
                    continue
                #--------------------
                # 布林軌道
                #--------------------
                # 計算上下軌道
                bband_up, bband, bband_down, msg = stock.getBBand()
                # 買入提示
                if realtime["now_price"] <= stock.buyPrice:
                    buyList.append (tmp)
                elif realtime["now_price"] >= bband_up*0.99 and realtime["pre_date_price"] <= bband_up*0.99:
                    bupstart.append (tmp)
                elif realtime["now_price"] >= bband_up*0.99:
                    bup.append (tmp)
                elif realtime["now_price"] <= bband_down*1.01 and realtime["pre_date_price"] >= bband_down*1.01:
                    bdownstart.append (tmp)
                elif realtime["now_price"] <= bband_down*1.01:
                    bdown.append (tmp)
                #--------------------
                # 跌幅排序
                #--------------------
                else:
                    if realtime["now_result_rate"] not in tmpDict:
                        tmpDict[realtime["now_result_rate"]] = []
                    tmpDict[realtime["now_result_rate"]].append (tmp)
            # 持有、權重都是直接印出來
            else:
                # 做印出來的動作
                printRealtimeStock (stockType, stock, g_removeList, realtime, True)
            # 做存起來的動作
            saveCache (removeCache, g_removeList)
        
        # 排列做處理
        if stockType == "做多" or stockType == "短期注意":
            if len(buyList) > 0:
                print ("=== 可買股 ===")
                for info in buyList:
                    if info == None:
                        continue
                    print (info)
            if len(bupstart) > 0:
                print ("=== 本日突破<布林軌道上緣> ===")
                for info in bupstart:
                    if info == None:
                        continue
                    print (info)
            if len(bup) > 0:
                print ("=== 突破<布林軌道上緣> ===")
                for info in bup:
                    if info == None:
                        continue
                    print (info)
            if len(bdownstart) > 0:
                print ("=== 今天跌破<布林軌道下緣> ===")
                for info in bdownstart:
                    if info == None:
                        continue
                    print (info)
            if len(bdown) > 0:
                print ("=== 跌破<布林軌道下緣> ===")
                for info in bdown:
                    if info == None:
                        continue
                    print (info)
            print ("=== 依跌幅排行 ===")
            tmpKeyList = [value for value in tmpDict.keys()]
            tmpKeyList.sort (reverse=False)
            for tmpKey in tmpKeyList:
                for info in tmpDict[tmpKey]:
                    if info == None:
                        continue
                    print (info)
        print ("")
    
    # 更新一下列表
    for stockType, stockMap in stockOrder.items():
        for removeStockID in g_removeList:
            if removeStockID in stockMap:
                stockMap.pop (removeStockID)

    # 提醒下次更新時間
    #break
    printCountDown (120)
