# DESC : 每天的股票日報
# DATE : 2020/11/23

import sys
sys.path.append(r"c:\download\ranb_gametowner\python_module")
from utility import *
sys.path.append (r"..\module")
from AllStockMgr import AllStockMgr
from NetStockInfo import NetStockInfo
import json

def getFromCache (stockID):
    filename = "../info/%s.txt" % (stockID,)
    if check_file (filename) == False:
        return {}
    file = open (filename, "r", encoding="utf-8")
    tmp = file.read ()
    file.close()
    return json.loads (tmp)

def saveCache (stockID, info):
    filename = "../info/%s.txt" % (stockID,)
    file = open (filename, "w", encoding="utf-8")
    file.writelines (json.dumps (info))
    file.close()

# 取得所有的股票
allstock = AllStockMgr.getAllStock ()
priorityKey = [
    "持有", 
    "核心", 
    "台積電概念股", 
    "被動元件", 
    "散熱", 
    "PCB", 
    "觀察", 
    "定存", 
    "看戲",
]

stockOrder = {}
for key in priorityKey:
    stockOrder[key] = {}

for stockID, stock in allstock.items():
    # 特別處理持有型股票
    if stock.holdPrice != 0:
        stockOrder["持有"][stockID] = stock
        continue
    for key, value in stockOrder.items():
        # 換個判定寫法
        #if stock.operationType == key:
        if stock.operationType.find (key) != -1:
            value[stockID] = stock
            break
    
# 清除暫存檔
#del_dir ("cache")
#check_dir ("cache")

file = open("../daily.txt", "w", encoding="utf-8")
def write (strFormat, *args):
    strtmp = (strFormat+"\n") % args
    print (strtmp, end="")
    file.writelines (strtmp)

# 依照重要性來做處理
for key in priorityKey:
    write ("#-------------------------------")
    write ("# %s", key)
    write ("#-------------------------------")
    # 一隻一隻去抓資料處理
    for stockID, stock in stockOrder[key].items():
        #------------------------
        # 寫入基本資料
        write ("#-------------------------------")
        write ("# %s(%s) 股本 %.2f 億", stockID, stock.name, stock.getInfoFloat ("股本"))
        write ("#-------------------------------")
        #------------------------
        # 今天的漲跌幅
        realtime = NetStockInfo.getYahooRealtime (stockID, False)
        #print (realtime)
        write ("[本日股價表現]")
        write ("%s %.1f %s", realtime["now_price"], realtime["now_result"], realtime["now_vol"])
        write ("")

        #------------------------
        # 最近五天3大法人動作
        write ("[近日三大法人動向]")
        for index in range (5):
            #write ("%s", json.dumps (stock.getInfo ("三大法人")[index]))
            write ("%s 外資:%s, 投信:%s", 
                stock.getInfo ("三大法人")[index]["date"], 
                stock.getInfo ("三大法人")[index]["out"], 
                stock.getInfo ("三大法人")[index]["in"],
            )
        write ("")

        #------------------------
        # 近三個月的營收
        write ("[最近月營收]")
        write ("%s 月增: %s %%, 年增: %s %%, 累計年增: %s %%", 
            stock.getInfo ("月營收", "2020/10", "年度/月份"),
            stock.getInfo ("月營收", "2020/10", "月增"),
            stock.getInfo ("月營收", "2020/10", "年増"),
            stock.getInfo ("月營收", "2020/10", "累計年增"),
        )
        write ("%s 月增: %s %%, 年增: %s %%, 累計年增: %s %%", 
            stock.getInfo ("月營收", "2020/09", "年度/月份"),
            stock.getInfo ("月營收", "2020/09", "月增"),
            stock.getInfo ("月營收", "2020/09", "年増"),
            stock.getInfo ("月營收", "2020/09", "累計年增"),
        )
        write ("%s 月增: %s %%, 年增: %s %%, 累計年增: %s %%", 
            stock.getInfo ("月營收", "2020/08", "年度/月份"),
            stock.getInfo ("月營收", "2020/08", "月增"),
            stock.getInfo ("月營收", "2020/08", "年増"),
            stock.getInfo ("月營收", "2020/08", "累計年增"),
        )
        write ("")

        #------------------------
        # 前三季 EPS
        write ("[2020前三季EPS]")
        write ("2020Q3 EPS:%s, 毛利率 : %s %%, 營業利益率 : %s %%, 稅前淨利率:%s %%",
            stock.getInfo ("QEPS", "2020Q3", "EPS"),
            stock.getInfo ("QEPS", "2020Q3", "毛利率"),
            stock.getInfo ("QEPS", "2020Q3", "營業利益率"),
            stock.getInfo ("QEPS", "2020Q3", "稅前淨利率"),
        )
        write ("2020Q2 EPS:%s, 毛利率 : %s %%, 營業利益率 : %s %%, 稅前淨利率:%s %%",
            stock.getInfo ("QEPS", "2020Q2", "EPS"),
            stock.getInfo ("QEPS", "2020Q2", "毛利率"),
            stock.getInfo ("QEPS", "2020Q2", "營業利益率"),
            stock.getInfo ("QEPS", "2020Q2", "稅前淨利率"),
        )
        write ("2020Q1 EPS:%s, 毛利率 : %s %%, 營業利益率 : %s %%, 稅前淨利率:%s %%",
            stock.getInfo ("QEPS", "2020Q1", "EPS"),
            stock.getInfo ("QEPS", "2020Q1", "毛利率"),
            stock.getInfo ("QEPS", "2020Q1", "營業利益率"),
            stock.getInfo ("QEPS", "2020Q1", "稅前淨利率"),
        )

        #------------------------
        # 去年EPS
        write ("2019 EPS : %s 元", stock.getInfo ("QEPS", "2019", "EPS"))
        write ("")

        #------------------------

    # 暫時只抓持有的
    #break

file.close()