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
    file = open ("error_Q.txt", "w", encoding="utf-8")
    for key, value in errorMap.items():
        file.writelines ("%s %s\n" % (key, value))
    file.close()

# 查詢資料, 並做儲存起來的動作
url_template = "https://histock.tw/stock/%s/每股盈餘"
for stockID, stock in allstock.items():
    print ("==[處理 %s]==" % (stockID,))
    filename = "../info/Q_EPS/%s.txt" % (stockID,)
    if check_file (filename) == True:
        print ("[ignore] info exist. " + filename)
        continue
    url = url_template % (stockID,)
    WebViewMgr.loadURL (url)
    # 先找年份 w1 w70
    source_nodes = WebViewMgr.getNodes ('//*[@class="w1 w70"]')
    year_list = []
    for node in source_nodes:
        #print ("~~")
        #print (node.text)
        year_list.append (node.text)
    year_list = year_list[1:]
    # 利用 xpath 找到資料
    source_nodes = WebViewMgr.getNodes ('//*[@class="tb-stock text-center tbBasic"]/tbody/tr/td')
    if len(source_nodes) == 0:
        print ("沒有資料", stock.id, stock.name)
        add_error (stock.id, stock.name)
        continue
    # 2012 ~ 2020 共9年
    info = {}
    for index, node in enumerate (source_nodes):
        Q = int(index / 9) + 1
        year_index = (index % 9)
        year = year_list[year_index]
        if year == "":
            continue
        #print (year, Q, node.text)
        if Q != 5:
            key = "%sQ%s" % (year, Q)
            info[key] = node.text
        else:
            key = "%s" % (year,)
            info[key] = node.text
    print (stock.name, info["2019"], info["2020"])
    # 寫入檔案
    file = open (filename, "w", encoding='utf-8')
    file.writelines (json.dumps (info))
    file.close()

WebViewMgr.close()
