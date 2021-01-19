# DESC : 用來更新所有資料
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
import csv

def getFromCache (stockID):
    filename = "../info/%s.txt" % (stockID,)
    if check_file (filename) == False:
        return {}
    file = open (filename, "r", encoding="utf-8")
    tmp = file.read ()
    file.close()
    return json.loads (tmp)

def saveCache (stockID, info):
    filename = "../info/%s.txt" % (stockID,)
    file = open (filename, "w", encoding="utf-8")
    file.writelines (json.dumps (info))
    file.close()

def getFromContinueCache (stockID):
    filename = "../info/%s_continue.txt" % (stockID,)
    if check_file (filename) == False:
        return {}
    file = open (filename, "r", encoding="utf-8")
    tmp = file.read ()
    file.close()
    return json.loads (tmp)

def saveContinueCache (stockID, info):
    filename = "../info/%s_continue.txt" % (stockID,)
    file = open (filename, "w", encoding="utf-8")
    file.writelines (json.dumps (info))
    file.close()

allstock = AllStockMgr.getAllStock ()
threeKey = "2021/01/19"

# 先取得 ../tmp 下的 csv 檔案
filelist = get_dir_file_list ("../tmp")
for filename in filelist:
    #---------------------
    # 處理上櫃的內容
    if filename.find ("BIGD_") != -1:
        file = open (filename, "r", encoding="utf-8")
        # for line in file:
            # line = line.strip ("\n ")
            # tokenList = line.split (",")
            # # 不是想要的就暫時不處理
            # if tokenList[0] not in allstock:
                # continue
            # if tokenList[0] != "3293":
                # continue
            # print (tokenList)
            # print (tokenList[6], tokenList[15], tokenList[38])
        reader = csv.reader(file, delimiter=',', quotechar='"')
        for row in reader:
            print (row)
        
        file.close()

































