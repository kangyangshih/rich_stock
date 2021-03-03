import sys
sys.path.append(r"c:\download\ranb_gametowner\python_module")
from utility import *
sys.path.append (r"..\module")
from AllStockMgr import AllStockMgr
from NetStockInfo import NetStockInfo
import json
import csv

# 取得所有的股票清單
allstock = AllStockMgr.getAllStock ()
for stockID, stock in allstock.items():
    # 載入暫存資料
    info = getFromCache ("../info/%s.txt" % (stockID,), {})
    for key , value in info["QEPS"].items():
        value["年度"] = key
    # 做存入的動作
    saveCache ("../info/%s.txt" % (stockID,), info)
    #break

