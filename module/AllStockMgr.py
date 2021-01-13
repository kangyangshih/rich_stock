# DESC : 用來管理股票相關的資料
# DATE : 2020/9/30

import sys
sys.path.append(r"c:\download\ranb_gametowner\python_module")
from utility import *
from excel_utility import *
import json
sys.path.append (r"..\module")
from NetStockInfo import NetStockInfo

#-----------------------------------------------------
# 單一股票
class cSingleStock :
    def __init__(self):
        # 股票編號
        self.id = ""
        # 股票名稱
        self.name = ""
        # 上巿/上櫃
        self.location = ""
        # 股票類型 : 股票 / ETF / 特別股
        self.type = ""
        # 操作類型
        self.operationType = ""
        # 最高參考價, 用來計算買點
        self.priceHigh = 0
        # 入手價
        self.buyPrice = 0
        # 空單價
        self.emptyPrice = 0
        # hold price
        self.holdPrice = 0
        # 賣出價
        self.sellPrice = 0
        # Tag
        self.tag = ""
        # 其他描述
        self.desc = ""
        self.netInfo = {}
    
    # 取得字串資訊
    def getInfo (self, *args):
        #print (args)
        # 取得直接參數
        if args[0] in self.__dict__:
            return self.__dict__[args[0]]
        # 取得網路參數
        target = self.netInfo
        #print (self.netInfo)
        for index in range (len(args)):
            if args[index] not in target:
                return None
            target = target[args[index]]
        return target
    
    # 取得資料, 轉成 INT
    def getInfoInt (self, *args):
        res = self.getInfo (*args)
        if res == None:
            return None
        return int(res.replace (",", ""))

    # 取得資料, 轉成浮點數    
    def getInfoFloat (self, *args):
        res = self.getInfo (*args)
        if res == None:
            return None
        return float (res.replace (",", ""))

    # 做寫入的動作
    def _write (self, file, res, strFormat, *args):
        # 串接字串
        strtmp = (strFormat+"\n") % args
        # 印到畫面上
        print (strtmp, end="")
        # 如果有需要寫檔就做寫入的動作
        if file != None:
            file.writelines (strtmp)
        # 把字串存起來
        res.append (strtmp)
    
    # 計算投本比、外本比
    def _getBuyRate (self, num):
        return (num / (self.getInfoFloat ("股本") * 10000))

    # 寫入單股資料
    def dumpInfo (self, file=None):
        res = []
        #------------------------
        # 寫入基本資料
        self._write (file, res, "#-------------------------------")
        self._write (file, res, "# %s(%s) 股本 %.2f 億", self.name, self.id, self.getInfoFloat ("股本"))
        self._write (file, res, "#-------------------------------")
        #------------------------
        # 今天的漲跌幅
        realtime = NetStockInfo.getYahooRealtime (self.id, False)
        #print (realtime)
        self._write (file, res, "[本日股價表現]")
        self._write (file, res, "%s %.1f 量 : %s", realtime["now_price"], realtime["now_result"], realtime["now_vol"])
        self._write (file, res, "")

        #------------------------
        # 持有價
        if self.holdPrice > 0:
            self._write (file, res, "[持有價] %s", self.holdPrice)
        # 買入價或是空單價
        if self.buyPrice > 0:
            self._write (file, res, "[買入價] %s", self.buyPrice)
        elif self.emptyPrice > 0:
            self._write (file, res, "[空單價] %s", self.emptyPrice)
        self._write (file, res, "")

        #------------------------
        # 個股簡評
        self._write (file, res, "[個股相關資訊] %s", self.future)
        # 分類類型
        self._write (file, res, self.operationType)

        if self.desc != "":
            self._write (file, res, self.desc)

        self._write (file, res, "")

        #------------------------
        # 可以加入自己的評價
        self._write (file, res, "[本日簡評]")
        # 2020 預估 EPS
        eps2020 = self._get2020EPS ()
        if eps2020 != None:
            self._write (file, res, "2020 預估全年 EPS : %.2f", eps2020)
        else:
            self._write (file, res, "無法預估2020 EPS")
            eps2020 = 0

        # 2021 預估配股配息和目前殖利率
        #print (self._getStockDividenRate())
        sd2021_money = eps2020 * self._getStockDividenRate() / 100
        self._write (file, res, "2021 預估配息 : %.2f 配息率 : %.2f %%", sd2021_money, self._getStockDividenRate())
        now_sd_rate = sd2021_money / realtime["now_price"] * 100
        self._write (file, res, "目前殖利率預估 : %.2f %%",  now_sd_rate)
        # 計算 6% 殖利率的價格
        if now_sd_rate < 6 and eps2020 > 0:
            target_price = sd2021_money / 0.06
            self._write (file, res, "[6%% 的買入價] : %.2f",  target_price)
        # 定存型股票多顯示8%買入價
        if eps2020 > 0 and self.future.find ("定存") != -1:
            target_price = sd2021_money / 0.08
            self._write (file, res, "[8%% 的買入價] : %.2f",  target_price)


        # 結束
        self._write (file, res, "")

        # 平均操作值
        #out_total, in_total = self._getThreeArg (1, 5, isABS=True)
        #self._write (file, res, "[近五日三大法人平均值] 外資: %.0f, 法人: %.0f\n", out_total, in_total)

        #------------------------
        # 最近五天3大法人動作
        #------------------------
        self._write (file, res, "[近日三大法人動向]")
        # 最近 15 天，三大法人買賣超數量
        out_total, in_total = self._getThreeTotal (15)
        out_total_rate = self._getBuyRate (out_total)
        in_total_rate = self._getBuyRate (in_total)
        # 判定最近一天的結果, 計算外本比，投本比
        # 外投比 2%->追蹤名單，3~6%->準備發動，
        # 1張=1000股，1=100%,一張面額=10元
        # 外本比
        today_out = float(self.getInfo ("三大法人")[0]["out"].replace(",", ""))
        #print (today_out, type(today_out))
        today_out_rate = self._getBuyRate (today_out)
        #print (today_out_rate, type(today_out_rate))
        self._write (file, res, "本日外資 : %.0f, 外本比:%.4f %%", today_out, today_out_rate)
        self._write (file, res, "近 15 日外資: %.0f, 外本比: %.4f %%\n", out_total, out_total_rate)
        # 投本比
        today_in = float(self.getInfo ("三大法人")[0]["in"].replace(",", ""))
        today_in_rate = self._getBuyRate (today_in)
        self._write (file, res, "本日投信 : %.0f, 投本比:%.4f %%", today_in, today_in_rate)
        self._write (file, res, "近 15 日投信: %.0f, 投本比: %.4f %%\n", in_total, in_total_rate)
        # 顯示近幾日結果
        for index in range (6):
            #self._write (file, res, "%s", json.dumps (self.getInfo ("三大法人")[index]))
            self._write (file, res, "%s 外資:%s, 投信:%s", 
                self.getInfo ("三大法人")[index]["date"], 
                self.getInfo ("三大法人")[index]["out"], 
                self.getInfo ("三大法人")[index]["in"],
            )
        self._write (file, res, "")

        #------------------------
        # 近三個月的營收
        self._write (file, res, "[最近月營收]")
        monthList = ["2020/12", "2020/11", "2020/10", "2020/09", "2020/08"]
        for month in monthList:
            if month not in self.netInfo["月營收"]:
                continue
            self._write (file, res, "%s 月營收:%.2f億, 月增: %s %%, 年增: %s %%, 累計年增: %s %%", 
                self.getInfo ("月營收", month, "年度/月份"),
                self.getInfoInt ("月營收", month, "月營收")/100000.0,
                self.getInfo ("月營收", month, "月增"),
                self.getInfo ("月營收", month, "年增"),
                self.getInfo ("月營收", month, "累計年增"),
            )
        self._write (file, res, "")

        #------------------------
        # 前三季 EPS
        self._write (file, res, "[2020前三季EPS]")
        quarterlyList = ["2020Q3", "2020Q2", "2020Q1"]
        for quarterly in quarterlyList:
            self._write (file, res, 
                "%s EPS:%s, 毛利率 : %s %%, 營業利益率 : %s %%, 稅前淨利率:%s %%",
                quarterly,
                self.getInfo ("QEPS", quarterly, "EPS"),
                self.getInfo ("QEPS", quarterly, "毛利率"),
                self.getInfo ("QEPS", quarterly, "營業利益率"),
                self.getInfo ("QEPS", quarterly, "稅前淨利率"),
            )

        #------------------------
        # 去年EPS
        self._write (file, res, "2019 EPS : %s 元", self.getInfo ("QEPS", "2019", "EPS"))
        self._write (file, res, "")

        #------------------------
        # 近幾年的配股配息
        self._write (file, res, "[配股配息]")
        sdList = self.getInfo ("配股配息")
        for index in range (5):
            # 不滿五年就不印了
            if index >= len(sdList):
                break
            self._write (file, res, 
                "%s EPS:%s, 股票股利:%s, 現金股利:%s, 配息率:%s",
                sdList[index]["所屬年度"],
                sdList[index]["EPS"],
                sdList[index]["股票股利"],
                sdList[index]["現金股利"],
                sdList[index]["配息率"],
            )
        self._write (file, res, "")

        #------------------------
        # 回傳結果
        return res

    #---------------------------------------
    # 依照過去的配息, 取得未來可能的配息率
    #---------------------------------------
    def _getStockDividenRate (self, years = 3):
        sdList = self.getInfo ("配股配息")
        sdRate = 0
        for index in range (years):
            # 不滿五年就不印了
            if index >= len(sdList):
                #print (len(sdList))
                #print (sdList)
                if index == 0:
                    return 0
                else:
                    return sdRate / (index)
            tmp = 0
            if sdList[index]["配息率"] != "-":
                tmp = float (sdList[index]["配息率"].replace ('%', ""))
            #mp = float (sdList[index]["配息率"].replace ('%', ""))
            # 配息超過 100 就算 100
            if tmp > 100:
                tmp = 100
            # 配息低於 0 就算 0
            if tmp < 0:
                tmp = 0
            sdRate += tmp
        # 回傳五年平低的結果
        return sdRate / years

    #---------------------------------------
    # 取得2020 EPS 預估    
    #---------------------------------------
    def _get2020EPS (self):
        if self.getInfo ("QEPS", "2020Q3", "EPS") != None and self.getInfo ("QEPS", "2020Q2", "EPS") != None and self.getInfo ("QEPS", "2020Q1", "EPS") != None:
            eps2020 = self.getInfoFloat ("QEPS", "2020Q3", "EPS") * 2 \
                    + self.getInfoFloat ("QEPS", "2020Q2", "EPS") \
                    + self.getInfoFloat ("QEPS", "2020Q1", "EPS")
            return eps2020
        else:
            return None
    
    #---------------------------------------
    # 取得近五年的外資買賣平均值
    #---------------------------------------
    def _getThreeArg (self, offset=0, counter=5, isABS=True):
        # 外資買賣超總額
        out_total = 0
        # 投信買賣超總額
        in_total = 0
        # 統計5日結果
        for index in range (offset, counter+offset):
            if isABS == False:
                out_total += float (self.getInfo ("三大法人")[index]["out"].replace (",", ""))
                in_total += float (self.getInfo ("三大法人")[index]["in"].replace (",", ""))
            else:
                out_total += abs(float (self.getInfo ("三大法人")[index]["out"].replace (",", "")))
                in_total += abs(float (self.getInfo ("三大法人")[index]["in"].replace (",", "")))
            #print (out_total, in_total)
        # 回傳平均結果
        return out_total/counter, in_total/counter
    
    #---------------------------------------
    # 取得指定時間的買賣超
    #---------------------------------------
    def _getThreeTotal (self, offset):
        # 外資買賣超總額
        out_total = 0
        # 投信買賣超總額
        in_total = 0
        # 統計指定區間的結果
        for index in range (0, offset):
            out_total += float (self.getInfo ("三大法人")[index]["out"].replace (",", ""))
            in_total += float (self.getInfo ("三大法人")[index]["in"].replace (",", ""))
        
        # 回傳平均結果
        return out_total, in_total

    #---------------------------------------
    # 取得外資買賣超
    #---------------------------------------
    def getOutBuySell (self):
        # 顯示近幾日結果
        out_list = [0, 0, 0]
        for index in range (5):
            # 處理外資的部分
            out_tmp = float (self.getInfo ("三大法人")[index]["out"].replace (",", ""))
            # 0 放買
            if out_tmp > 0:
                out_list[0] += 1
            # 1 放賣
            elif out_tmp < 0:
                out_list[1] += 1
            # 2 放總值
            out_list[2] += out_tmp
        if out_list[2] > 0:
            return out_list[0], out_list[2]
        if out_list[2] < 0:
            return -out_list[1], out_list[2]
        return 0, 0
    
    #---------------------------------------
    # 取得投信買賣超
    #---------------------------------------
    def getInBuySell (self):
        # 顯示近幾日結果
        in_list = [0, 0, 0]
        for index in range (5):
            # 處理投信的部分
            in_tmp = float (self.getInfo ("三大法人")[index]["in"].replace (",", ""))
            # 0 放買
            if in_tmp > 0:
                in_list[0] += 1
            # 1 放賣
            elif in_tmp < 0:
                in_list[1] += 1
            # 2 放總值
            in_list[2] += in_tmp
        if in_list[2] > 0:
            return in_list[0], in_list[2]
        if in_list[2] < 0:
            return -in_list[1], in_list[2]
        return 0, 0
            
#-----------------------------------------------------
# 股票管理器
class cAllStockMgr:
    def __loadJsonFromFile (self, filename):
        file = open (filename, "r", encoding="utf-8")
        tmp = file.read ()
        file.close()
        return json.loads (tmp)

    def __init__(self):
        # 存放所有的股票列表
        self.stockMap = {}
        # 載入股票
        self.__loadAllStock ()

    # 載入所有股票資訊
    def __loadAllStock (self):
        print ("[cStockMgr][__loadAllStock] start")
        res, tmp2020 = getFromCache ("../info/eps_2020.txt")
        #print (tmp2020)
        excel = getExcelSheet ("../all_stock.xlsx", "all_stock")
        for row_index in range (1, 5000):
            if excel.getValue (row_index, 0, None) == None:
                print ("結束嚕, 共有 " + str(len(self.stockMap)))
                break
            #print (row_index)
            # 取得相關資料
            single = cSingleStock()
            # 代碼
            single.id =  excel.getValue (row_index, 0, "", str)
            # 名稱
            single.name = excel.getValue(row_index, 1)
            # 上巿/上櫃
            single.location = excel.getValue(row_index, 2)
            # ETF / 股票 / 特別股
            single.type = excel.getValue(row_index, 3)
            # [看法]
            # 核心
            # 觀察
            # 看戲
            # 定存
            single.operationType = excel.getValue(row_index, 4)
            single.future = excel.getValue (row_index, 5)
            # 買入價
            single.buyPrice = excel.getValue (row_index, 6, 0, int)
            single.emptyPrice = excel.getValue (row_index, 7, 0, int)
            # 持有價
            single.holdPrice = excel.getValue (row_index, 8, 0, float)
            # 停損價
            single.sellPrice = excel.getValue (row_index, 9, 0, int)
            # 標籤
            single.tag = excel.getValue (row_index, 10).replace ("%", "%%")
            # 雜項
            single.desc = excel.getValue (row_index, 11).replace ("%", "%%")
            # 不取得DR
            if single.name.endswith ("-DR") == True:
                continue
            # 取得資訊
            infoFilename = "../info/%s.txt" % (single.id,)
            # 沒有個人資訊也不做處理
            if check_file(infoFilename) == True:
                tmp, single.netInfo = getFromCache (infoFilename)
            if single.id in tmp2020:
                single.netInfo.update (tmp2020[single.id])
            # 記錄起來
            self.stockMap[single.id] = single

    # 取得所有的股票列表
    def getAllStock (self, isNeedNetInfo=False):
        res = {}
        for key, value in self.stockMap.items():
            # 不是股票不回傳
            if value.type != "股票":
                #print ("[ignore][不是股票] "+value.name)
                continue
            # 沒有網路資訊不做回傳
            if isNeedNetInfo == True and len(value.netInfo) == 0:
                #print ("[ignore][isNeedNetInfo] "+value.name)
                continue
            res[key] = value
        return res
    
    # 取得想要及時查看的股票列表
    def getRealTimeStock (self):
        res = {}
        for key, value in self.stockMap.items():
            # 沒有買入價就不看
            if value.buyPrice == 0:
                continue
            #print ("[%s] %s weight:%d" % (value.id, value.name, value.weight))
            res[value.id] = value
        print ("[getRealTimeStock] 共有 %d 筆" % (len(res),))
        return res


# 實作 singleton
AllStockMgr = cAllStockMgr()
