# 來猜測一下 2020 的 eps 吧??

# 載入所有 python 共用模組
import sys
sys.path.append(r"c:\download\ranb_gametowner\python_module")
from utility import *
# 載入這個專案共用模組
sys.path.append (r"..\module")
from AllStockMgr import AllStockMgr
import json

msgList = []
def writeMsg (strFormat, *args):
    msg = strFormat % args
    msgList.append (msg)
    file = open ("../stock_2020_eps.txt", "w", encoding="utf-8")
    for line in msgList:
        file.writelines (line + "\n")
    file.close()

# 取得所有的股票
allStock = AllStockMgr.getAllStock ()

# 一檔一檔去寫
for stockID, stock in allStock.items():
    # 每檔股票做處理
    writeMsg ("==== %s =====", stock.name)
    
    # 目前只做一檔
    break


