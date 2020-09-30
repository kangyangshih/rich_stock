# DESC : 及時行情監控, 股票, 還有其他行情
# DATE : 2020/9/22

import time
import os
import sys
sys.path.append(r"c:\download\ranb_gametowner\python_module")
# 載入常用工具
from utility import *
# 載入自己寫的模組
sys.path.append(r"../module")
# 載入股票管理器
from AllStockMgr import AllStockMgr
# 從 Yahoo 抓取及時的報價
from YahooRealTimeMgr import YahooRealTimeMgr

# 取得想要監看的股票
realMap = AllStockMgr.getRealTimeStock ()

# 不斷一直做
while True:
    # 顯示大盤
    res = YahooRealTimeMgr._get_TAIEX()
    #print ("[%s] %s %s %s 億" % (res["pos"], res["total_point"], res["total_change_value"], res["total_vol"]))
    #print (YahooRealTimeMgr.get_OTC())
    # 顯示大盤
    #res = YahooRealTimeMgr.get_OTC()
    #print ("[%s] %s %s %s 億" % (res["pos"], res["total_point"], res["total_change_value"], res["total_vol"]))

    # 顯示股票
    break
