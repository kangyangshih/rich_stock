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
priorityKey = ["持有", "核心", "觀察", "定存", "看戲"]
stockOrder = {}
for key in priorityKey:
    stockOrder[key] = {}

for stockID, stock in allstock.items():
    # 特別處理持有型股票
    if stock.holdPrice != 0:
        stockOrder["持有"][stockID] = stock
        continue
    for key, value in stockOrder.items():
        if stock.operationType == key:
            value[stockID] = stock
            break
    
# 清除暫存檔
del_dir ("cache")
check_dir ("cache")

file = open("../daily.txt", "w", encoding="utf-8")
def write (strFormat, *args):
    file.writelines ((strFormat+"\n") % args)
# 依照重要性來做處理
for key in priorityKey:
    file.writelines ("#-------------------------------\n")
    file.writelines ("# %s\n" % (key,))
    file.writelines ("#-------------------------------\n")
    # 一隻一隻去抓資料處理
    for stockID, stock in stockOrder[key].items():
        file.writelines

    # 暫時只抓持有的
    break

file.close()