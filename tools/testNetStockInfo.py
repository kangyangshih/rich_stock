# DESC : 用來取得每一季的EPS
# DATE : 20202/10/15

# 載入所有 python 共用模組
import sys
sys.path.append(r"c:\download\ranb_gametowner\python_module")
from utility import *
#WebViewMgr.debugMode ()
# 載入這個專案共用模組
sys.path.append (r"..\module")
from AllStockMgr import AllStockMgr
from NetStockInfo import NetStockInfo
import json

# 取得所有的股票清單
allstock = AllStockMgr.getAllStock ()
for stockID, stock in allstock.items():
    print (NetStockInfo.getYahooRealtime (stockID, False))
    print (NetStockInfo.getHistockQEPS (stockID))
    break

