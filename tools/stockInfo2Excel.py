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

def isFloat (tmp):
    try:
        float(tmp)
    except ValueError:
        return False
    return True

#---------------------------
# 取得有資訊的股票
#---------------------------
allStock = AllStockMgr.getAllStock (True)

row_index = 0
col_index = 0
cell_format_multiline = wb.add_format(
    {
        # 自動換行的動作
        'text_wrap': True,
        # 置中
        'align' : "center",
        # 垂直置中
        'valign' : "vcenter",
    }
)
cell_format = wb.add_format(
    {
        # 置中
        'align' : "center",
        # 垂直置中
        'valign' : "vcenter",
    }
)
def writeInfo (*args):
    global col_index
    for index in range (len(args)):
        info = args[index]
        # 做型別處理
        if isinstance (info, str) == True and info.isdigit () == True:
            info = int(info)
        elif isinstance (info, str) == True and isFloat (info) == True:
            info = float (info)
        # 做欄位的處理
        if isinstance (info, str) == True and info.find ("\n") != -1:
            ws.write (row_index, col_index, info, cell_format_multiline)
        # 如果是0就不寫入
        elif isinstance (info, int) == True and info == 0:
            pass
        else:
            ws.write (row_index, col_index, info, cell_format)
        col_index = col_index + 1

# 寫入標題
writeInfo ("編號", "名稱", "淨值", "近期高價", "買入價", "持有價", "停損價"
    , "2019\nEPS"
    , "2020Q1\n營業額", "EPS", "2020Q1 三率"
    , "2020Q2\n營業額", "EPS", "2020Q2 三率"
    , "2020Q3\n營業額", "2020Q3\n估EPS", "2020\n估EPS"
    , "雜項"
)
# 往下一行寫入
col_index = 0
row_index = 1

# 一檔一檔去寫
for stockID, stock in allStock.items():
    col_index = 0
    # 編號, 名稱, 近期高價, 買入價, 賣出價, 雜項, 2019EPS, 2019配息配股, 2020Q1, 2020Q2, 2020估Q3, 2020估EPS
    writeInfo (stock.id, stock.name, stock.getInfo ("淨值"), stock.priceHigh, stock.buyPrice, stock.holdPrice, stock.sellPrice)
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
    # 雜項
    writeInfo (stock.desc)
    # 換到下一行    
    row_index = row_index + 1

# 做關閉的動作
wb.close()




