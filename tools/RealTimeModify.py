# 做及時的報價, 目前每一分鐘一次
# DESC : 2020/11/2

# Todo
# 急漲急跌的股票?

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
    "及時",
    "短期注意",
    "做多",
    "做空",
]

stockOrder = {}
for key in priorityKey:
    stockOrder[key] = {}

# 把想要監控的做一下分類
for stockID, stock in allstock.items():
    if stock.holdPrice != 0:
        stockOrder["持有"][stockID] = stock
        continue
    if stock.future.find ("及時") != -1:
        stockOrder["及時"][stockID] =  stock
        continue
    if stock.future.find ("短期注意") != -1:
        stockOrder["短期注意"][stockID] =  stock
        continue
    if stock.buyPrice != 0:
        stockOrder["做多"][stockID] = stock
        continue

# 肯定是要刪目錄的        
#del_dir ("cache")
#check_dir ("cache")

# 印出來結果
def printRealtimeStock (stockType, stock, removeList):
    # 取得及時資訊
    realtime = NetStockInfo.getYahooRealtime (stock.id, realtime=False)
    #------------------------------
    if stockType == "持有":
        #print (stock.holdPrice, type(stock.holdPrice))
        # 鈊象(3293) 770(750) -3.0 4,950 
        command = "%s(%s) %s(%s) %.1f %s" % (
            stock.name, 
            stock.id, 
            realtime["now_price"], 
            stock.holdPrice,
            realtime["now_result"], 
            realtime["now_vol"],
        )
        print (command)
        return

    #------------------------------
    if stockType == "及時":
        # 鈊象(3293) 770 -3.0 4,950 
        command = "%s(%s) %s %.1f %s" % (
            stock.name, 
            stock.id, 
            realtime["now_price"], 
            realtime["now_result"], 
            realtime["now_vol"],
        )
        print (command)
        return

    #------------------------------
    if stockType == "短期注意":
        if stock.buyPrice == 0:
            command = "%s(%s) %s %.1f %s" % (
                stock.name, 
                stock.id, 
                realtime["now_price"], 
                realtime["now_result"], 
                realtime["now_vol"],
            )
            print (command)
        else:
            command = "%s(%s) %s(%s) %.1f %s" % (
                stock.name, 
                stock.id, 
                realtime["now_price"], 
                stock.buyPrice,
                realtime["now_result"], 
                realtime["now_vol"],
            )
            print (command)
        return

    #------------------------------
    # 做多的，以盡量靠近為主
    if stockType == "做多":
        #print ("=========")
        #print ("%s %s %s %s" % (stock.name, stock.id, realtime["now_price"], stock.buyPrice))
        # 如果差太遠就先不理他
        if realtime["now_price"] * 0.9 > stock.buyPrice:
            #print ("%s(%s) 現價(%s)和買價(%s)差太遠, 不列入及時" % (stock.name, stock.id, realtime["now_price"], stock.buyPrice))
            removeList.append (stockID)
            return
        command = "%s(%s) %s(%s) %.1f %s" % (
            stock.name, 
            stock.id, 
            realtime["now_price"], 
            stock.buyPrice,
            realtime["now_result"], 
            realtime["now_vol"],
        )
        print (command)
        return

#------------------------------
# 做一個定時更新的動作
while True:
    # 先清除畫面
    clear_console ()
    # 抓取想要更新的股票
    removeList = []
    for stockType, stockMap in stockOrder.items():
        print ("=======%s=======" % (stockType,))
        for stockID, stock in stockMap.items():
            # 做印出來的動作
            printRealtimeStock (stockType, stock, removeList)
        print ("")
    # 提醒下次更新時間
    break
