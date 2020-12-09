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
    "定存", 
    "電腦選",
    "台積電", 
    "被動元件", 
    "工具機",
    "聯發科",
    "散熱", 
    "PCB", 
    "Tesla",
    "太陽能",
    "Mini LED",
    "衛星",
    "觀察", 
    "看戲",
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