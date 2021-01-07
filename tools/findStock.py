import sys
sys.path.append(r"c:\download\ranb_gametowner\python_module")
from utility import *
sys.path.append (r"..\module")
from AllStockMgr import AllStockMgr
from NetStockInfo import NetStockInfo
import json

# 取得所有的股票
allstock = AllStockMgr.getAllStock ()

for stockID, stock in allstock.items():
    pass


