# DESC : 把現有資料轉成 excel
# pip install xlsxwriter

#---------------------------
# 載入所有 python 共用模組
#---------------------------
import sys
sys.path.append(r"c:\download\ranb_gametowner\python_module")
from utility import *
# 載入這個專案共用模組
sys.path.append (r"..\module")
from AllStockMgr import AllStockMgr
from RealTimeMgr import RealTimeMgr
import json
import xlsxwriter

#---------------------------
# 做檔案檢查
#---------------------------
excelFilename = "../all_stock_info.xlsx"
if check_file (excelFilename) == True:
    del_file (excelFilename)
# 建立一個excel檔案
wb = xlsxwriter.Workbook(excelFilename)
# 建立一個 all 的表
ws = wb.add_worksheet("all") 

#---------------------------
# 取得有資訊的股票
#---------------------------
allStock = AllStockMgr.getAllStock (True)

row_index = 0
col_index = 0
def writeInfo (info):
    global col_index
    ws.write (row_index, col_index, info)
    col_index = col_index + 1

# 一檔一檔去寫
for stockID, stock in allStock.items():
    col_index = 0
    # 編號, 名稱, 近期高價, 買入價, 賣出價, 雜項, 2019EPS, 2019配息配股, 2020Q1, 2020Q2, 2020估Q3, 2020估EPS
    writeInfo (stock.id)
    writeInfo (stock.name)
    writeInfo (stock.getInfo ("淨值"))
    writeInfo (stock.priceHigh)
    writeInfo (stock.buyPrice)
    writeInfo (stock.sellPrice)
    writeInfo (stock.desc)
    # 2019
    writeInfo (stock.getInfo ("QEPS", "2019", "EPS"))
    # 2020Q1
    writeInfo (stock.getInfo ("TurnOver_2020Q1"))
    writeInfo (stock.getInfo ("QEPS", "2020Q1", "EPS"))
    writeInfo ("毛利率 : %s\n營業利益率 : %s\n稅前淨利率:%s" % (
        stock.getInfo ("QEPS", "2020Q1", "毛利率"),
        stock.getInfo ("QEPS", "2020Q1", "營業利益率"),
        stock.getInfo ("QEPS", "2020Q1", "稅前淨利率"),
    ))
    # 2020Q2
    writeInfo (stock.getInfo ("TurnOver_2020Q2"))
    writeInfo (stock.getInfo ("QEPS", "2020Q2", "EPS"))
    writeInfo ("毛利率 : %s\n營業利益率 : %s\n稅前淨利率:%s" % (
        stock.getInfo ("QEPS", "2020Q2", "毛利率"),
        stock.getInfo ("QEPS", "2020Q2", "營業利益率"),
        stock.getInfo ("QEPS", "2020Q2", "稅前淨利率"),
    ))
    # 2020Q3
    writeInfo (stock.getInfo ("TurnOver_2020Q3"))
    writeInfo (stock.getInfo ("2020Q3"))
    # 2020
    writeInfo (stock.getInfo ("EPS2020"))
    # 換到下一行    
    row_index = row_index + 1

# 做關閉的動作
wb.close()




