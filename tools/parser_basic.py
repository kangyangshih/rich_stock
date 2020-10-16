
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
check_dir ("../info/basic/")
errorMap = {}
def add_error (id, name):
    errorMap[id] = name
    file = open ("error_basic.txt", "w", encoding="utf-8")
    for key, value in errorMap.items():
        file.writelines ("%s %s\n" % (key, value))
    file.close()

allStockMap = {}
def add_single (stockID, info, isSave=True):
    if stockID != None:
        allStockMap[stockID] = info
    if isSave == True:
        file = open ("../info/basic.txt", 'w', encoding="utf-8")
        file.writelines (json.dumps(allStockMap))
        file.close()

# 查詢資料, 並做儲存起來的動作
url_template = "https://tw.stock.yahoo.com/d/s/company_%s.html"
for stockID, stock in allstock.items():
    print ("==[處理 %s]==" % (stockID,))
    filename = "../info/basic/%s.txt" % (stockID,)
    if check_file (filename) == True:
        print ("[ignore] info exist. " + filename)
        # 讀檔出來, 並加入股票
        file = open (filename, "r", encoding="utf-8")
        info = json.loads (file.read())
        file.close()
        add_single (stockID, info, False)
        continue
    
    url = url_template % (stockID,)
    WebViewMgr.loadURL (url)
    #WebViewMgr.savePage ("tmp.html")
    info = {}
    # 取得股本位置
    equity = WebViewMgr.getText ('/html/body/table[1]/tbody/tr[2]/td/table[1]/tbody/tr[8]/td[2]')
    equity = equity.strip ("\n億")
    info["股本"] = equity
    # 每股淨值
    netAssetValue = WebViewMgr.getText ('/html/body/table[1]/tbody/tr[2]/td/table[2]/tbody/tr[6]/td[3]')
    # 每股淨值: 　　32.38元
    netAssetValue = netAssetValue.replace ("每股淨值:", "").replace (" ", "").replace ("　", "")
    netAssetValue = netAssetValue.strip ("元")
    #print (netAssetValue)
    info["淨值"] = netAssetValue
    # 寫入檔案
    file = open (filename, "w", encoding='utf-8')
    file.writelines (json.dumps (info))
    file.close()
    add_single (stockID, info, False)
    #break

WebViewMgr.close()
add_single (None, None, True)
