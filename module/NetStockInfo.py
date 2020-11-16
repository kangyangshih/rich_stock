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
    
    #--------------------------------------------
    # 從 Yahoo 取得基本資料
    #--------------------------------------------
    def getYahooBasic (self, stockID, info):
        #  如果有股本就暫不處理
        if "股本" in info:
            return {}
        url_template = "https://tw.stock.yahoo.com/d/s/company_%s.html"
        url = url_template % (stockID,)
        print ("[getYahooBasic] " + url)
        WebViewMgr.loadURL (url)
        info = {}
        # 取得股本位置
        equity = WebViewMgr.getText ('/html/body/table[1]/tbody/tr[2]/td/table[1]/tbody/tr[8]/td[2]')
        # 如果載入失敗就等10秒再重載入
        if equity == None:
            time.sleep (30)
            return self.getYahooBasic (stockID)
        equity = equity.strip ("\n億")
        info["股本"] = equity
        # 每股淨值
        netAssetValue = WebViewMgr.getText ('/html/body/table[1]/tbody/tr[2]/td/table[2]/tbody/tr[6]/td[3]')
        # 每股淨值: 　　32.38元
        netAssetValue = netAssetValue.replace ("每股淨值:", "").replace (" ", "").replace ("　", "")
        netAssetValue = netAssetValue.strip ("元")
        #print (netAssetValue)
        info["淨值"] = netAssetValue
        # 回傳結果
        return info
    
    #--------------------------------------------
    # 從 Yahoo 取得及時資訊
    #--------------------------------------------
    def getYahooRealtime (self, stockID, realtime=False):
        stockID = str(stockID)
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
        html_text = get_url ("https://tw.stock.yahoo.com/q/q?s="+stockID, "cache/%s.html" % (stockID,) if realtime == False else "")
        soup = BeautifulSoup(html_text, "html.parser")
        info_list = soup.find_all ("td", bgcolor="#FFFfff")
        result = {"id":stockID}
        for index in range(len(info_list)):
            if index >= len(name_list):
                break
            #print ("name:%s, value:%s" % (name_list[index], info_list[index].string))
            result[name_list[index]] = info_list[index].string
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

    #--------------------------------------------
    # 從 Histock 取得每季的EPS資訊
    #--------------------------------------------
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
            print ("沒有資料", stockID)
            return False, {}
 
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
        return True, info

    #--------------------------------------------
    # 從 HiStock 取得月營收資料
    #--------------------------------------------
    def getHistockTurnOver (self, stockID):
        url_template = "https://histock.tw/stock/%s/財務報表"
        url = url_template % (stockID,)
        WebViewMgr.loadURL (url)
        # 利用 xpath 找到東西
        source_nodes = WebViewMgr.getNodes ('//*[@class="tb-stock text-center tbBasic"]/tbody/tr/td')
        if len(source_nodes) == 0:
            print ("沒有資料", stockID)
            return False, {}
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
        # 回傳結果
        return True, info

    #--------------------------------------------
    # 從 Histock 取得流動比和速動比
    # 流動比率一般要求是要在200%以上，越高越好，代表短期在還債上越沒有壓力。
    # 速動比率一般要求是要在100%以上
    #--------------------------------------------
    def getHistockLSRate (self, stockID):
        url_template = "https://histock.tw/stock/%s/流速動比率"
        url = url_template % (stockID,)
        WebViewMgr.loadURL (url)
        # 利用 xpath 找到東西
        source_nodes = WebViewMgr.getNodes ('//*[@class="tb-stock tbBasic"]/tbody/tr/td')
        if len(source_nodes) == 0:
            print ("沒有資料", stockID)
            return False, {}
        # 2018/1 ~ 2020/9
        info = {}
        # 年度/季別	流動比	速動比
        for index in range (0, 100):
            rowIndex = index * 3
            if rowIndex >= len(source_nodes):
                break
            res = {}
            res["年度/季別"] = source_nodes[rowIndex].text
            res["流動比"] = source_nodes[rowIndex+1].text.replace ("%", "")
            res["速動比"] = source_nodes[rowIndex+2].text.replace ("%", "")
            info[res["年度/季別"]] = res
        # 回傳結果
        return True, info



NetStockInfo = cNetStockInfo ()
