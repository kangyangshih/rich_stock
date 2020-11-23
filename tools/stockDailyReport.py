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
# 清除暫存檔
#del_dir ("cache")
#check_dir ("cache")

file = open("daily.txt", "w", encoding="utf-8")
# 先輸出持有股票
for stockID, stock in allstock.items():
    # 不是持有股票就暫時不需要查看
    if stock.holdPrice == 0:
        continue
    # 載入暫存資料
    info = getFromCache (stockID)
    # 寫入標題
    file.writelines ("=== [%s] %s ===\n" % (stock.id, stock.name))
    # 寫入今天的結果
    info = NetStockInfo.getYahooRealtime (stockID, False)
    # 

file.close()