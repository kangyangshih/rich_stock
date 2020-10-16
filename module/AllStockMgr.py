# DESC : 用來管理股票相關的資料
# DATE : 2020/9/30

import sys
sys.path.append(r"c:\download\ranb_gametowner\python_module")
from utility import *
from excel_utility import *

# 單一股票
class cSingleStock :
    def __init__(self):
        # 股票編號
        self.id = ""
        # 股票名稱
        self.name = ""
        # 上巿/上櫃
        self.location = ""
        # 股票類型 : 股票 / ETF / 特別股
        self.type = ""
        # 最高參考價, 用來計算買點
        self.priceHigh = 0
        # 入手價
        self.buyPrice = 0
        # 賣出價
        self.sellPrice = 0
        # Tag
        self.tag = ""
        # 其他描述
        self.desc = ""
    
# 股票管理器
class cAllStockMgr:
    def __init__(self):
        # 存放所有的股票列表
        self.stockMap = {}
        # 載入股票
        self.__loadAllStock ()

    # 載入所有股票資訊
    def __loadAllStock (self):
        print ("[cStockMgr][__loadAllStock] start")
        excel = getExcelSheet ("../all_stock.xlsx", "all_stock")
        for row_index in range (1, 5000):
            if excel.getValue (row_index, 0, None) == None:
                print ("結束嚕, 共有 " + str(len(self.stockMap)))
                break
            #print (row_index)
            # 取得相關資料
            single = cSingleStock()
            # 代碼
            single.id =  excel.getValue (row_index, 0, "", str)
            # 名稱
            single.name = excel.getValue(row_index, 1)
            # 上巿/上櫃
            single.location = excel.getValue(row_index, 2)
            # ETF / 股票 / 特別股
            single.type = excel.getValue(row_index, 3)
            # 近期高價
            single.priceHigh = excel.getValue (row_index, 4, 0, int)
            # 買入價
            single.buyPrice = excel.getValue (row_index, 5, 0, int)
            # 賣出價
            single.sellPrice = excel.getValue (row_index, 6, 0, int)
            # 標籤
            single.tag = excel.getValue (row_index, 7)
            # 雜項
            single.desc = excel.getValue (row_index, 8)
            # 不取得DR
            if single.name.endswith ("-DR") == True:
                continue
            # 記錄起來
            self.stockMap[single.id] = single

    # 取得所有的股票列表
    def getAllStock (self):
        res = {}
        for key, value in self.stockMap.items():
            if value.type != "股票":
                continue
            res[key] = value
        return res
    
    # 取得想要及時查看的股票列表
    def getRealTimeStock (self):
        res = {}
        for key, value in self.stockMap.items():
            # 沒有買入價就不看
            if value.buyPrice == 0:
                continue
            #print ("[%s] %s weight:%d" % (value.id, value.name, value.weight))
            res[value.id] = value
        print ("[getRealTimeStock] 共有 %d 筆" % (len(res),))
        return res

    # 取得單月營收
    def getStockTurnRate (self, stockID, key):
        pass
    
    # 取得單季 EPS / 全年EPS
    def getStockQEPS (self, stockID, key):
        pass

# 實作 singleton
AllStockMgr = cAllStockMgr()
