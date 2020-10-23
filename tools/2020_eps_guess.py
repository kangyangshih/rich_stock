# 來猜測一下 2020 的 eps 吧??

# 載入所有 python 共用模組
import sys
sys.path.append(r"c:\download\ranb_gametowner\python_module")
from utility import *
# 載入這個專案共用模組
sys.path.append (r"..\module")
from AllStockMgr import AllStockMgr
from RealTimeMgr import RealTimeMgr
import json

msgList = []
def writeMsg (strFormat, *args):
    msg = strFormat % args
    msgList.append (msg)

def saveMsg ():
    file = open ("../stock_2020_eps.txt", "w", encoding="utf-8")
    for line in msgList:
        file.writelines (line + "\n")
    file.close()

# 取得有資訊的股票
allStock = AllStockMgr.getAllStock (True)

infoMap = {}

# 一檔一檔去寫
for stockID, stock in allStock.items():
    info = {}
    # 每檔股票做處理
    print ("=== 產出 %s, %s ===" % (stock.id, stock.name))
    writeMsg ("==== %s %s =====", stockID, stock.name)
    value = stock.getInfoFloat ("股本")
    writeMsg ("股本 : %.2f 億", value)
    writeMsg ("每股淨值 : %s 元", stock.getInfo ("淨值"))
    writeMsg ("=== 2019 EPS ===")
    writeMsg ("2019 EPS : %s 元", stock.getInfo ("QEPS", "2019"))
    # 2020Q1
    writeMsg ("=== 2020 EPS ===")
    TurnOver_2020Q1 = stock.getInfoInt ("月營收", "2020/01", "月營收") + \
                      stock.getInfoInt ("月營收", "2020/02", "月營收") + \
                      stock.getInfoInt ("月營收", "2020/03", "月營收")
    #print (TurnOver_2020Q1)
    TurnOver_2020Q1 = TurnOver_2020Q1 / 100000.0
    info["TurnOver_2020Q1"] = TurnOver_2020Q1
    if TurnOver_2020Q1 == 0:
        continue
    #  毛利的取得
    earnRate = stock.getInfoFloat ("QEPS", "2020Q1", "稅前淨利率")
    writeMsg ("2020Q1 營收 : %3.2f億, EPS : %2.2f 元, 淨利 : %2.2f", TurnOver_2020Q1, stock.getInfoFloat ("QEPS", "2020Q1", "EPS"), earnRate)
    # 2020Q2
    TurnOver_2020Q2 = stock.getInfoInt ("月營收", "2020/04", "月營收") + \
                      stock.getInfoInt ("月營收", "2020/05", "月營收") + \
                      stock.getInfoInt ("月營收", "2020/06", "月營收")
    TurnOver_2020Q2 = TurnOver_2020Q2 / 100000.0
    info["TurnOver_2020Q2"] = TurnOver_2020Q2
    if TurnOver_2020Q2 == 0:
        continue
    #  毛利的計算
    earnRate = stock.getInfoFloat ("QEPS", "2020Q2", "稅前淨利率")
    info["earnRate"] = earnRate
    writeMsg ("2020Q2 營收 : %3.2f億, EPS : %2.2f 元, 淨利 : %2.2f", TurnOver_2020Q2, stock.getInfoFloat ("QEPS", "2020Q2", "EPS"), earnRate)

    # 2020Q3 預估
    writeMsg ("=2020Q3 EPS=")
    # 7月
    TurnOver_7 = stock.getInfoInt ("月營收", "2020/07", "月營收") / 100000.0
    eps_7 = TurnOver_7 / value * 10 * earnRate / 100
    info["TurnOver_7"] = TurnOver_7
    info["eps_7"] = eps_7
    writeMsg ("2020 7月 營收 %3.2f億, 估 EPS : %2.2f元", TurnOver_7, eps_7)
    TurnOver_8 = stock.getInfoInt ("月營收", "2020/08", "月營收") / 100000.0
    eps_8 = TurnOver_8 / value * 10 * earnRate / 100
    info["TurnOver_8"] = TurnOver_8
    info["eps_8"] = eps_8
    writeMsg ("2020 8月 營收 %3.2f億, 估 EPS : %2.2f元", TurnOver_8, eps_8)
    # 9月
    TurnOver_9 = stock.getInfoInt ("月營收", "2020/09", "月營收") / 100000.0
    eps_9 = TurnOver_9 / value * 10 * earnRate / 100
    info["TurnOver_9"] = TurnOver_9
    info["eps_9"] = eps_9
    writeMsg ("2020 9月 營收 %3.2f億, 估 EPS : %2.2f元", TurnOver_9, eps_9)
    TurnOver_2020Q3 = TurnOver_7 + TurnOver_8 + TurnOver_9
    EPSQ3 = eps_7 + eps_8 + eps_9
    info["TurnOver_2020Q3"] = TurnOver_2020Q3
    writeMsg ("2020Q3 營收 : %3.2f億, 估EPS : %2.2f 元", TurnOver_2020Q3, EPSQ3)
    # 2020 全年EPS估
    writeMsg ("=2020 估 EPS=")
    EPS2020 = stock.getInfoFloat ("QEPS", "2020Q1", "EPS") + \
              stock.getInfoFloat ("QEPS", "2020Q2", "EPS") + \
              EPSQ3 + EPSQ3
    info["EPS2020"] = EPS2020
    # 目前股價 / 本益比
    res = RealTimeMgr.get_stock (stockID)
    tmp = 0
    if EPS2020 > 0:
        tmp = res["now_price"] / EPS2020
    info["本益比"] = tmp
    msg = "現價 : %3.2f, 估EPS : %2.2f 元, 本益比 : %.1f\n" % ( res["now_price"], EPS2020, tmp)
    writeMsg (msg)
    print (msg)
    saveMsg()
    infoMap[stockID] = info
    # 目前只做一檔
    #break

file = open ("../info/2020_eps.txt", "w", encoding="utf-8")
file.writelines (json.dumps (infoMap))
file.close()

