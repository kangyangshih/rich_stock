# 取得每年的配股配息 (未完成)


# DESC : 用來取得每一季的EPS
# DATE : 20202/10/15

# 載入所有 python 共用模組
import sys
sys.path.append(r"c:\download\ranb_gametowner\python_module")
from utility import *
from WebViewMgr import WebViewMgr
#WebViewMgr.debugMode ()
# 載入這個專案共用模組
sys.path.append (r"..\module")
from AllStockMgr import AllStockMgr
import json

# 取得所有的股票清單
allstock = AllStockMgr.getAllStock ()
check_dir ("../info/dividend/")
errorMap = {}
def add_error (id, name):
    errorMap[id] = name
    file = open ("error_dividend.txt", "w", encoding="utf-8")
    for key, value in errorMap.items():
        file.writelines ("%s %s\n" % (key, value))
    file.close()

allStockMap = {}
def add_single (stockID, info, isSave=True):
    if stockID != None:
        allStockMap[stockID] = info
    if isSave == True:
        file = open ("../info/dividend.txt", 'w', encoding="utf-8")
        file.writelines (json.dumps(allStockMap))
        file.close()

# 查詢資料, 並做儲存起來的動作
url_template = "https://goodinfo.tw/StockInfo/StockDividendPolicy.asp?STOCK_ID=%s"
for stockID, stock in allstock.items():
    if stockID != "3293":
        continue
    print ("==[處理 %s]==" % (stockID,))
    filename = "../info/dividend/%s.txt" % (stockID,)
    #if check_file (filename) == True:
    #    print ("[ignore] info exist. " + filename)
    #    # 讀檔出來, 並加入股票
    #    file = open (filename, "r", encoding="utf-8")
    #    info = json.loads (file.read())
    #    file.close()
    #    add_single (stockID, info, False)
    #    continue
    
    url = url_template % (stockID,)
    WebViewMgr.loadURL (url)
    #WebViewMgr.savePage ("tmp.html")
    info = {}
    # 取得一整行
    rowNodes = WebViewMgr.getNodes ('//*[@id="divDetail"]/table/tbody[1]/tr')
    for rowNode in rowNodes:
        print ("~~~~~~~~")
        nodes = rowNode.find_elements_by_xpath ('.//td')
        tmp_list = []
        for node in nodes:
            print (node.text)
            tmp_list.append (node.text)
        # 取得想要的資料
        tmp = {}
        tmp["年度"] = tmp_list[0]
        tmp["股利"] = tmp_list[1]
        tmp["股票"] = tmp_list[2]
        break
    # 寫入檔案
    #file = open (filename, "w", encoding='utf-8')
    #file.writelines (json.dumps (info))
    #file.close()
    #add_single (stockID, info, False)
    break

#WebViewMgr.close()
add_single (None, None, True)
