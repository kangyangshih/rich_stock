# DESC : 取得一些網路資料

import sys
sys.path.append(r"c:\download\ranb_gametowner\python_module")
from utility import *
from excel_utility import *
import json
from WebViewMgr import WebViewMgr
from bs4 import BeautifulSoup
from lxml import etree

class cNetStockInfo:

    def __init__(self):
        pass
    
    # 取得及時資訊
    def getYahooRealtime (self, stock_id, realtime=False):
        stock_id = str(stock_id)
        name_list = [
            # 更新時間
            "update_time"
            # 現在價錢
            , "now_price"
            # 漲跌值
            , "now_result"
            , "buy_price"
            , "sell_price"
            # 量能
            , "now_num"
            , "pre_date_price"
            , "start_price"
            # 最高價
            , "max_price"
            # 最低價
            , "min_price"
        ]
        now_time = time.gmtime()
        # 從 yahoo 取得
        html_text = get_url ("https://tw.stock.yahoo.com/q/q?s="+stock_id, "cache/%s.html" % (stock_id,) if realtime == True else "")
        soup = BeautifulSoup(html_text, "html.parser")
        info_list = soup.find_all ("td", bgcolor="#FFFfff")
        result = {"id":stock_id}
        for index in range(len(info_list)):
            if index >= len(name_list):
                break
            #print ("name:%s, value:%s" % (name_list[index], info_list[index].string))
            result[name_list[index]] = info_list[index].string
        #print ("stock_id:", stock_id)
        #print (result)
        if (result["now_price"] == "-"):
            result["now_result"] = 0
            result["now_num"] = "0"
            result["min_price"] = result["pre_date_price"]
            result["max_price"] = result["pre_date_price"]
            result["now_price"] = result["pre_date_price"]
            result["start_price"] = result["pre_date_price"]
        else:
            result["now_result"] = float(result["now_price"]) - float(result["pre_date_price"])
        # 處理數量
        result["now_vol"] = int (result["now_num"].replace (",", ""))
        # 處理型別
        result["now_price"] = float(result["now_price"])
        # 回傳結果
        return result

    # 取得每季的EPS資訊
    def getHistockQEPS (self, stockID):
        #------------------------------
        # 取得每股盈餘
        #------------------------------
        url_template = "https://histock.tw/stock/%s/每股盈餘"
        url = url_template % (stockID,)
        WebViewMgr.loadURL (url)
        # 先找年份 w1 w70
        source_nodes = WebViewMgr.getNodes ('//*[@class="w1 w70"]')
        year_list = []
        for node in source_nodes:
            year_list.append (node.text)
        year_list = year_list[1:]
        # 利用 xpath 找到資料
        source_nodes = WebViewMgr.getNodes ('//*[@class="tb-stock text-center tbBasic"]/tbody/tr/td')
        if len(source_nodes) == 0:
            print ("沒有資料", stock.id, stock.name)
            return {}
 
        # 2012 ~ 2020 共9年
        info = {}
        for index, node in enumerate (source_nodes):
            Q = int(index / 9) + 1
            year_index = (index % 9)
            year = year_list[year_index]
            if year == "":
                continue
            key = ""
            if Q != 5:
                key = "%sQ%s" % (year, Q)
            else:
                key = "%s" % (year,)
            # 取得內容設定
            info[key] = {
                "EPS" : node.text,
                "毛利率" : None,
                "營業利益率" : None,
                "稅前淨利率" : None,
                "稅後淨利率" : None,
            }
        
        #------------------------------
        # 取得 EPS 的其他資訊
        #------------------------------
        url_template = "https://histock.tw/stock/%s/利潤比率"
        url = url_template % (stockID,)
        WebViewMgr.loadURL (url)
        # 找詢資料
        source_nodes = WebViewMgr.getNodes ('//*[@class="tb-stock tbBasic"]/tbody/tr')
        #print (len(source_nodes))
        for source_node in source_nodes:
            nodes = source_node.find_elements_by_xpath ('.//td')
            if len(nodes) == 0:
                continue
            #print (len(nodes))
            tmpList = []
            for node in nodes:
                #print (node.text)
                tmpList.append (node.text)
            if tmpList[0] in info:
                info[tmpList[0]]["毛利率"] = tmpList[1].replace ("%", "")
                info[tmpList[0]]["營業利益率"] = tmpList[2].replace ("%", "")
                info[tmpList[0]]["稅前淨利率"] = tmpList[3].replace ("%", "")
                info[tmpList[0]]["稅後淨利率"] = tmpList[4].replace ("%", "")

        # 把一些沒有在使用的拿掉
        removeKeyList = []
        for key, value in info.items():
            if value["毛利率"] == None and key.find ("Q") != -1:
                print ("%s 沒有毛利，先移除" % (key,))
                #info.pop (key)
                removeKeyList.append (key)

        for key in removeKeyList:
            info.pop(key)

        #print (info)
        # 回傳結果
        return info

NetStockInfo = cNetStockInfo ()
