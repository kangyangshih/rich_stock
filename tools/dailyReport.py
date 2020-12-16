# DESC : 每天的股票日報
# DATE : 2020/11/23

import sys
sys.path.append(r"c:\download\ranb_gametowner\python_module")
from utility import *
sys.path.append (r"..\module")
from AllStockMgr import AllStockMgr
from NetStockInfo import NetStockInfo
import json

# 清除暫存檔
#del_dir ("cache")
#check_dir ("cache")

# 取得所有的股票
allstock = AllStockMgr.getAllStock ()
priorityKey = [
    "持有", 
    "核心", 
    "衛星",
    "定存", 
    "電腦選",
    "阮老師",
    "老師選",
    "遊戲",
    "鑽針",
    "通路",
    "台積電", 
    "聯電",
    "鴻海",
    "華為",
    "矽晶圓",
    "Apple",
    "被動元件", 
    "工具機",
    "聯發科",
    "散熱",
    "PCB", 
    "Tesla",
    "太陽能",
    "風電",
    "Mini-LED",
    "PC",
    "電信",
    "面板",
    "封測廠", 
    "口罩",
    "手套",
    "自行車",
    "汽車",
    "車用",
    "資產",
    "健身器材",
    "紡織",
    "通路",
    "電源供應器",
    "資料中心",
    "光學鏡頭廠",
    "金融股",
    "電機機械",
    "觀察",
    "雜項",
]

stockOrder = {}
for key in priorityKey:
    stockOrder[key] = {}

for stockID, stock in allstock.items():
    # 特別處理持有型股票
    if stock.holdPrice != 0:
        stockOrder["持有"][stockID] = stock
        continue
    # 如果有在裏面, 就依照順序
    isOrder = False
    for key, value in stockOrder.items():
        # 換個判定寫法
        #if stock.operationType == key:
        if stock.operationType.find (key) != -1:
            value[stockID] = stock
            isOrder = True
            break
    # 如果沒在裏面就放在最後
    if isOrder == False and stock.operationType != "":
        stockOrder["雜項"][stockID] = stock
    
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

        # 把資料 dump 下來
        stock.dumpInfo (file)
        #print (res)

        # 暫時只先抓一隻
        #break
        
    # 暫時只抓持有的
    #break

file.close()