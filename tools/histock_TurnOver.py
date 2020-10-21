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

errorMap = {}
def add_error (id, name):
    errorMap[id] = name
    file = open ("error_TurnOver.txt", "w", encoding="utf-8")
    for key, value in errorMap.items():
        file.writelines ("%s %s\n" % (key, value))
    file.close()

allStockMap = {}
def add_single (stockID, info, isSave=True):
    if stockID != None:
        allStockMap[stockID] = info
    if isSave == True:
        file = open ("../info/TurnOver.txt", 'w', encoding="utf-8")
        file.writelines (json.dumps(allStockMap))
        file.close()

# 查詢資料, 並做儲存起來的動作
url_template = "https://histock.tw/stock/%s/財務報表"
for stockID, stock in allstock.items():
    print ("==[處理 %s]==" % (stockID,))
    filename = "../info/TurnOver/%s.txt" % (stockID,)
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
    # 利用 xpath 找到東西
    source_nodes = WebViewMgr.getNodes ('//*[@class="tb-stock text-center tbBasic"]/tbody/tr/td')
    if len(source_nodes) == 0:
        print ("沒有資料", stock.id, stock.name)
        add_error (stock.id, stock.name)
        continue
    # 2018/1 ~ 2020/9
    info = {}
    # 月份/單月/去年/單月月增/單月年增/累計/去年累計/累計年增
    for index in range (0, 100):
        rowIndex = index * 8
        if rowIndex >= len(source_nodes):
            break
        res = {}
        res["年度/月份"] = source_nodes[rowIndex].text
        # 千元為單位
        res["月營收"] = source_nodes[rowIndex+1].text.replace (",", "")
        res["月增"] = source_nodes[rowIndex+3].text.replace ("%", "")
        res["年増"] = source_nodes[rowIndex+4].text.replace ("%", "")
        res["累計營收"] = source_nodes[rowIndex+5].text.replace (",", "")
        res["累計年增"] = source_nodes[rowIndex+7].text.replace("%", "")
        #print (res["年度/月份"])
        info[res["年度/月份"]] = res
    print (stock.name, info["2020/09"]["月營收"], info["2020/09"]["年増"], info["2020/09"]["累計年增"])
    # 寫入檔案
    file = open (filename, "w", encoding='utf-8')
    file.writelines (json.dumps (info))
    file.close()
    #break
    add_single (stockID, info, False)

WebViewMgr.close()
add_single (None, None, True)
