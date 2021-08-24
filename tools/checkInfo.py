# DESC : allstock.xlxs 裏沒有的股票，把暫存檔刪除。

import sys
sys.path.append(r"..\..\ranb_gametowner\python_module")
from utility import *
#WebViewMgr.debugMode ()
# 載入這個專案共用模組
sys.path.append (r"..\module")
from AllStockMgr import AllStockMgr
from NetStockInfo import NetStockInfo
import json
import csv

# 取得所有的股票
allstock = AllStockMgr.getAllStock ()

#-----------------------------
# 處理被移除掉的資料
#-----------------------------
print ("== 處理被移除 excel 的檔案 ==")
# 取得目錄下的檔案
dirFileList = get_dir_file_list ("../info")

# 取得被刪除的檔案，做刪除的動作
for stockID, stock in allstock.items():
    tmp = "../info/%s.txt" % (stockID,)
    if tmp in dirFileList:
        dirFileList.remove (tmp)

print ("需要被移除的列表:", dirFileList)
for removeFile in dirFileList:
    del_file (removeFile)
