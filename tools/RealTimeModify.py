# 做及時的報價, 目前每一分鐘一次
# DESC : 2020/11/2

# Todo
# 急漲急跌的股票?

#---------------------------
# 載入所有 python 共用模組
#---------------------------
import sys
sys.path.append(r"c:\download\ranb_gametowner\python_module")
from utility import *
# 載入這個專案共用模組
sys.path.append (r"..\module")
from AllStockMgr import AllStockMgr
from NetStockInfo import NetStockInfo
import json

# 取得所有的股票
allstock = AllStockMgr.getAllStock ()
priorityKey = [
    "持有", 
    "做多",
    "做空",
]

stockOrder = {}
for key in priorityKey:
    stockOrder[key] = {}

# 把想要監控的做一下分類
for stockID, stock in allstock.items():
    pass

# 做一個定時更新的動作
while True:

    # 抓取想要更新的股票

    # 持有股

    # 接近買進目標價 5% 的

    # 接近放空目錄價 5% 的

    # 核心股

    # 提醒下次更新時間
    pass
