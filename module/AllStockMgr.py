# DESC : 用來管理股票相關的資料
# DATE : 2020/9/30

import sys
sys.path.append(r"c:\download\ranb_gametowner\python_module")
from utility import *
from excel_utility import *
import json
sys.path.append (r"..\module")
from NetStockInfo import NetStockInfo
from StockDBMgr import StockDBMgr

#-----------------------------------------------------
# 單一股票
class cSingleStock :
    # 日期的排序
    dayKeyList = []
    # 做初使化的動作
    def __init__(self):
        # 股票編號
        self.id = ""
        # 股票名稱
        self.name = ""
        # 上巿/上櫃
        self.location = ""
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
        # 2021 配息
        self.sd2021 = ""
        self.sd2021_stock = 0
        # 其他描述
        self.desc = ""
        self.netInfo = {}
        # 2020 公告的EPS
        self.EPS2020 = None
    
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
    
    # 取得指定天的均線
    def _getdayInfoAvg (self, infoKey, dayShift, rangeNum):
        if dayShift + rangeNum >= len(self.netInfo["daily"]):
            return None
        res = 0
        for index in range (dayShift, dayShift + rangeNum):
            res += self.netInfo["daily"][index][infoKey]
        res = res / rangeNum
        return res
    
    # 取得 MA
    def getdayPriceAvg (self, dayKey, rangeNum):
        return self._getdayInfoAvg ("end_price", dayKey, rangeNum)
    
    # 取得乖離率 (Bias Rate(BIAS))
    def getdayBIAS (self, rangeNum):
        # 取得 MA5
        MA = self.getdayPriceAvg (0, rangeNum)
        # 取得今天的資料
        info = self.getTodayPrice (0)
        # N日乖離率＝（當日收盤價－N日移動平均價）÷N日移動平均價×100%
        res = (info["end_price"]-MA)/MA * 100
        # 正乖離過大
        if res >= 15:
            return res, "正乖離過大，要小心拉回"
        # 負乖離過大
        if res <= -15:
            return res, "負乖離過大，可能有反彈"
        return res, ""
    
    # 取得布林通道
    def getBBand (self, rangeNum=20, rate=2):
        #------------------------
        # 取得MA
        MA = self.getdayPriceAvg (0, rangeNum)
        #------------------------
        # 取得標準差
        tmp = 0
        # 取得差數平方數
        for index in range (rangeNum):
            info = self.getTodayPrice (index)
            #MA = self.getdayPriceAvg (index, rangeNum)
            tmp += (info["end_price"] - MA) ** 2
        # 均值
        tmp = tmp / rangeNum
        # 開根號
        tmp = tmp ** 0.5
        # 取得評價
        msg = ""
        info = self.getTodayPrice (0)
        if info["end_price"] < MA:
            msg += "股價處於弱勢\n"
        else:
            msg += "股價處理強勢\n"
        infoPre = self.getTodayPrice (1)
        MA20Pre = self.getdayPriceAvg (1, rangeNum)
        # 黃金交叉
        if infoPre["end_price"] < MA20Pre and info["end_price"] > MA:
            msg += "價格由下向上，升穿下軌線，可伺機逢低買入\n"
        # 死亡交叉
        if infoPre["end_price"] > MA20Pre and info["end_price"] < MA:
            msg += "價格由上向下，跌破中軌線，可伺機逢高賣出\n"
        
        # 突破上下緣
        if info["end_price"] > MA+tmp*rate:
            msg += "超級強勢，要小心出場時間"
        elif info["end_price"] < MA - tmp*rate:
            msg += "超級弱勢，可以準備進場"
        
        #------------------------
        # 取得 bband
        return MA + tmp*rate, MA, MA - tmp*rate, msg

    # 取得平均量
    def getdayVolAvg (self, dayKey, rangeNum):
        return self._getdayInfoAvg ("vol", dayKey, rangeNum)
    
    # 取得當天資訊
    def getTodayPrice (self, dayShift=0):
        return self.netInfo["daily"][dayShift]

    # 取得均線是否排列好
    def isMASorted (self):
        tmp5 = self.getdayPriceAvg (0, 5)
        tmp20 = self.getdayPriceAvg (0, 20)
        tmp60 = self.getdayPriceAvg (0, 60)
        if tmp5 > tmp20 and tmp20 > tmp60:
            return True
        return False
    
    # 轉換張數 -> 股本比，用來計算投本比、外本比
    def _getBuyRate (self, num):
        return (num / (self.getInfoFloat ("股本") * 10000))

    # 取得一些常講的技術線型
    def specialMA (self):
        # 取得今天的 20/60 MA
        MA20 = self.getdayPriceAvg (0, 20)
        MA60 = self.getdayPriceAvg (0, 60)
        # 取得昨天的 20/60 MA
        MA20Pre = self.getdayPriceAvg (1, 20)
        MA60Pre = self.getdayPriceAvg (1, 60)
        # 黃金交叉
        if MA20Pre < MA60Pre and MA20 > MA60:
            return 1, "黃金交叉"
        # 死亡交叉
        if MA20Pre > MA60Pre and MA20 < MA60:
            return 2, "死亡交叉"
        # 什麼都沒有
        return 0, ""
    
    # 取得個股的描述
    def getDesc (self):
        sourceRes = self.desc
        res = ""
        tail = ""
        # 去除掉一些不必要的資料
        lineToken = sourceRes.split ("\n")
        for line in lineToken:
            # 直接加入
            res += line + "\n"
        # 回傳頭+尾
        return res + tail
    
    # 每季的賺錢類型
    def getQBusinessType (self):
        if self.QBType.find ("平均") != -1:
            return "平均"
        if self.QBType.find ("成長") != -1:
            return "成長"
        if self.QBType.find ("累加") != -1:
            return "累加"
        return None
    
    # 寫入單股資料
    def dumpInfo (self, file=None):
        res = []
        realtime = self.getTodayPrice ()
        if realtime["end_price"] == 0:
            return res
        #------------------------
        # 寫入基本資料
        self._write (file, res, "#-------------------------------")
        self._write (file, res, "# %s(%s) %s 股本 %.2f 億", self.name, self.id, self.location, self.getInfoFloat ("股本"))
        self._write (file, res, "# %s", self.getInfo ("產業類別"))
        self._write (file, res, "#-------------------------------")
        #------------------------
        # 營業比重
        self._write (file, res, "%s", self.getInfo ("營業比重"))
        self._write (file, res, "")
        
        #------------------------
        # 持有價
        if self.holdPrice > 0:
            self._write (file, res, "[持有價] %s", self.holdPrice)
        # 買入價或是空單價
        if self.buyPrice > 0:
            self._write (file, res, "[手動設定買入價] %s", self.buyPrice)
        elif self.emptyPrice > 0:
            self._write (file, res, "[手動設定空單價] %s", self.emptyPrice)
        self._write (file, res, "")

        #------------------------
        # 今天的漲跌幅
        self._write (file, res, "[本日股價表現]")
        self._write (file, res, 
            "%s(%s~%s) %.1f 量 : %s (5日均量:%.1f)", 
            realtime["end_price"], 
            realtime["low_price"],
            realtime["high_price"],
            realtime["diff"], 
            realtime["vol"], 
            self.getdayVolAvg(0, 5)
        )

        self._write (file, res, "")

        #------------------------
        self._write (file, res, "[EPS/殖利率表現]")
        # 2021 預估 EPS
        if self.getInfo ("QEPS", "2021Q1", "EPS") != None \
            and self.getInfo ("QEPS", "2020Q2", "EPS") != None \
            and self.getInfo ("QEPS", "2020Q1", "EPS") != None \
            and self.getInfoFloat ("QEPS", "2020Q1", "EPS") != 0:
            # 2021Q1 的EPS
            eps2021Q1 = self.getInfoFloat ("QEPS", "2021Q1", "EPS")
            eps2020Q1 = self.getInfoFloat ("QEPS", "2020Q1", "EPS")
            uprate = eps2021Q1 / eps2020Q1
            # 預估 EPS
            eps2021Q1Q4EPST1 = self.getInfoFloat ("QEPS", "2021Q1", "EPS") \
                + (self.getInfoFloat ("QEPS", "2020Q2", "EPS") \
                + self.getInfoFloat ("QEPS", "2020Q4", "EPS") \
                + self.getInfoFloat ("QEPS", "2020Q3", "EPS") ) * uprate
            eps2021Q1Q4EPST2 = self.getInfoFloat ("QEPS", "2021Q1", "EPS") \
                + (self.getInfoFloat ("QEPS", "2020Q2", "EPS") \
                + self.getInfoFloat ("QEPS", "2020Q4", "EPS") \
                + self.getInfoFloat ("QEPS", "2020Q3", "EPS") )
            eps2021Q1Q4EPST3 = self.getInfoFloat ("QEPS", "2021Q1", "EPS") * 4
            # 依照不同的商業類型做修改
            #self._write (file , res, "%s -> %s", self.QBType, self.getQBusinessType())
            if self.getQBusinessType () == "成長":
                self._write (file, res, "2021Q1 EPS %s(%s), 估 EPS/配息 : 【成長】%.2f/%.2f" % (
                    self.getInfo ("QEPS", "2021Q1", "EPS"), 
                    self.getInfo ("QEPS", "2020Q1", "EPS"), 
                    eps2021Q1Q4EPST1,
                    eps2021Q1Q4EPST1 * self._getStockDividenRate() / 100,
                ))
            elif self.getQBusinessType() == "累加":
                self._write (file, res, "2021Q1 EPS %s(%s), 估 EPS/配息 : 【累加】%.2f/%.2f " % (
                    self.getInfo ("QEPS", "2021Q1", "EPS"), 
                    self.getInfo ("QEPS", "2020Q1", "EPS"), 
                    eps2021Q1Q4EPST2,
                    eps2021Q1Q4EPST2 * self._getStockDividenRate() / 100,
                ))
            elif self.getQBusinessType() == "平均":
                self._write (file, res, "2021Q1 EPS %s(%s), 估 EPS/配息 : 【平均】 %.2f/%.2f" % (
                    self.getInfo ("QEPS", "2021Q1", "EPS"), 
                    self.getInfo ("QEPS", "2020Q1", "EPS"), 
                    eps2021Q1Q4EPST3,
                    eps2021Q1Q4EPST3 * self._getStockDividenRate() / 100,
                ))
            else:
                self._write (file, res, "2021Q1 EPS %s(%s), 估 EPS/配息 : 【成長】%.2f/%.2f 【累加】%.2f/%.2f 【平均】 %.2f/%.2f)" % (
                    self.getInfo ("QEPS", "2021Q1", "EPS"), 
                    self.getInfo ("QEPS", "2020Q1", "EPS"), 
                    eps2021Q1Q4EPST1,
                    eps2021Q1Q4EPST1 * self._getStockDividenRate() / 100,
                    eps2021Q1Q4EPST2,
                    eps2021Q1Q4EPST2 * self._getStockDividenRate() / 100,
                    eps2021Q1Q4EPST3,
                    eps2021Q1Q4EPST3 * self._getStockDividenRate() / 100,
                ))
        else:
            self._write (file, res, "暫時無法估 2021 EPS")
        # 2020 預估 EPS
        tmp, eps2020 = self._get2020EPS ()
        if tmp == 3:
            self._write (file, res, "無法預估2020 EPS")
            eps2020 = 0
        elif tmp == 0:
            self._write (file, res, "【公告】2020 全年EPS : %.2f", eps2020)
        elif tmp == 1:
            self._write (file, res, "2020 新聞公告EPS : %.2f", eps2020)
        else:
            self._write (file, res, "2020 預估全年 EPS : %.2f", eps2020)
        if eps2020 != None:
            # 2021 預估配股配息和目前殖利率
            sd2021_money = self.sd2021
            if sd2021_money == None:
                sd2021_money = eps2020 * self._getStockDividenRate() / 100
                self._write (file, res, "2021 預估配息 : %.2f 配息率 : %.2f %%", sd2021_money, self._getStockDividenRate())
            else:
                self._write (file, res, "2021 公告配息 : %.2f 配股:%.2f 配息率 : %.2f %%", sd2021_money, self.sd2021_stock,  (sd2021_money+self.sd2021_stock)/eps2020*100 if eps2020 != 0 else 0)
            now_sd_rate = sd2021_money / realtime["end_price"] * 100 + self.sd2021_stock * 10
            self._write (file, res, "目前 %.2f 殖利率預估 : %.2f %%",  realtime["end_price"], now_sd_rate)
            # 計算 6% 殖利率的價格
            if sd2021_money > 0 or self.sd2021_stock > 0:
                target_price = sd2021_money / (0.06-(self.sd2021_stock+0.00001)/10)
                self._write (file, res, "[6%% 的買入價] : %.2f",  target_price)
                # 定存型股票多顯示8%買入價
                target_price = sd2021_money / (0.08-(self.sd2021_stock+0.00001)/10)
                self._write (file, res, "[8%% 的買入價] : %.2f",  target_price)
            else:
                self._write (file, res, "[警告] 無法評估買入價")
        else:
            self._write (file, res, "[警告] 無法評估買入價")

        self._write (file, res, "")
        #------------------------
        self._write (file, res, "[技術分析數據]")
        # 顯示布林通道
        bband_up, bband, bband_down, msg = self.getBBand ()
        self._write (file, res, "布林通道: (%.1f, %.1f, %.1f)\n%s", bband_up, bband, bband_down, msg)
        # 移動平均線 (周線/月線/季線)
        self._write (file, res, "")
        self._write (file, res, "[均線是否排好] %s", self.isMASorted())
        for index in (5, 20, 60):
            # 當天均線
            tmp = self.getdayPriceAvg (0, index)
            # 前一天均線
            preTmp = self.getdayPriceAvg (1, index)
            # 趨勢
            trend = "↑"
            if tmp < preTmp:
                trend = "↓"
            # BIAS
            bias, msg = self.getdayBIAS (index)
            if index <= 20:
                self._write (file, res, "MA%s : %.2f %s 乖離率:%.2f%% %s", index, tmp, trend, bias, msg)
            else:
                self._write (file, res, "MA%s : %.2f %s 乖離率:%.2f%%", index, tmp, trend, bias)
            # 跌破X日線
            if realtime["pre_price"] > tmp and realtime["end_price"] < tmp:
                self._write (file, res, "<跌破 %s 日線>" % (index,))
        self._write (file, res, "")

        #------------------------
        # 技術線型
        self._write (file, res, "[技術線型]")
        self._write (file ,res, "技術線型區: https://stock.pchome.com.tw/stock/sto0/ock1/sid%s.html" % (self.id,))
        # 是黃金交叉還是死亡交叉
        specialMAType, tmp = self.specialMA ()
        if specialMAType > 0:
            self._write (file, res, tmp)
        # 結束
        self._write (file, res, "")

        #------------------------
        # 個股簡評
        self._write (file, res, "[個股相關資訊] %s", self.future.replace ("\n", "、"))
        # 描述
        if self.desc != "":
            self._write (file, res, self.getDesc())
        self._write (file, res, "")

        #------------------------
        # 可以加入自己的評價
        self._write (file, res, "[本日簡評]")

        # 結束
        self._write (file, res, "")

        #------------------------
        # 最近五天3大法人動作
        #------------------------
        self._write (file, res, "[近日三大法人動向]")
        # 外本比
        today_out = self.getInfo ("三大法人")[0]["out"]
        today_out_rate = self._getBuyRate (today_out)
        self._write (file, res, "本日外資 : %.0f, 外本比:%.4f %%", today_out, today_out_rate)
        for day in (5, 20, 60):
            # 最近 15 天，三大法人買賣超數量
            out_total, in_total = self._getThreeTotal (day)
            out_total_rate = self._getBuyRate (out_total)
            # 判定最近一天的結果, 計算外本比，投本比
            # 外投比 2%->追蹤名單，3~6%->準備發動，
            # 1張=1000股，1=100%,一張面額=10元
            # 外本比
            self._write (file, res, "近 %s 日外資: %.0f, 外本比: %.4f %%", day, out_total, out_total_rate)
        self._write (file, res, "")
        
        # 投本比
        today_in = self.getInfo ("三大法人")[0]["credit"]
        today_in_rate = self._getBuyRate (today_in)
        self._write (file, res, "本日投信 : %.0f, 投本比:%.4f %%", today_in, today_in_rate)
        for day in (5, 20, 60):
            # 最近 15 天，三大法人買賣超數量
            out_total, in_total = self._getThreeTotal (day)
            in_total_rate = self._getBuyRate (in_total)
            # 判定最近一天的結果, 計算外本比，投本比
            # 外投比 2%->追蹤名單，3~6%->準備發動，
            # 1張=1000股，1=100%,一張面額=10元
            # 投本比
            self._write (file, res, "近 %s 日投信: %.0f, 投本比: %.4f %%", day, in_total, in_total_rate)
        self._write (file, res, "")

        # 顯示近幾日結果
        for index in range (6):
            #self._write (file, res, "%s", json.dumps (self.getInfo ("三大法人")[index]))
            self._write (file, res, "%s 外資:%s(%s,%s), 投信:%s(%s,%s), 自營商(自行):%s, 自營商(避險):%s", 
                self.getInfo ("三大法人")[index]["date"], 
                self.getInfo ("三大法人")[index]["out"],
                self.getInfo ("三大法人")[index]["out_buy"],
                self.getInfo ("三大法人")[index]["out_sell"],
                self.getInfo ("三大法人")[index]["credit"],
                self.getInfo ("三大法人")[index]["credit_buy"],
                self.getInfo ("三大法人")[index]["credit_sell"],
                self.getInfo ("三大法人")[index]["self_0"],
                self.getInfo ("三大法人")[index]["self_1"],
            )
        self._write (file, res, "")

        #------------------------
        # 近幾個月的營收
        self._write (file, res, "[最近月營收]")
        monthNum = 13
        tmpList = changeDict2List (self.netInfo["月營收"])
        for index in range (monthNum):
            month = tmpList[index]["年度/月份"]
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
        self._write (file, res, "[前四季EPS]")
        # 先計算2021Q1 的平均營收
        total = 0
        counter = 0
        for monthIndex in ["2021/04", "2021/05", "2021/06"]:
            if self.getInfoInt ("月營收", monthIndex, "月營收") == None:
                break
            total += self.getInfoInt ("月營收", monthIndex, "月營收")/100000.0
            counter += 1
        self._write (file, res, "2021Q2 季營收: %.2f 億, 平均月營收: %.2f 億" %(total, total/counter))
        # 顯示近4季EPS
        QEPSNum = 0
        tmpList = changeDict2List (self.netInfo["QEPS"])
        for index in range (100):
            if index >= len(tmpList):
                break
            quarterly = tmpList[index]["年度"]
            #print (index, tmpList[index]["年度"])
            if quarterly.find ("Q") == -1:
                continue
            QEPSNum += 1
            if QEPSNum > 5:
                break
            if self.getInfo ("QEPS", quarterly, "季營收") == None:
                break
            print (index, tmpList[index]["年度"])
            self._write (file, res, 
                "%s EPS:%s, 季營收: %.2f 億, 平均月營收: %.2f 億, 平均月EPS: %.2f, 毛利率 : %s %%, 營業利益率 : %s %%, 稅前淨利率:%s %%",
                quarterly,
                self.getInfo ("QEPS", quarterly, "EPS"),
                self.getInfo ("QEPS", quarterly, "季營收"),
                self.getInfo ("QEPS", quarterly, "平均月營收"),
                self.getInfo ("QEPS", quarterly, "MEPS"),
                self.getInfo ("QEPS", quarterly, "毛利率"),
                self.getInfo ("QEPS", quarterly, "營業利益率"),
                self.getInfo ("QEPS", quarterly, "稅前淨利率"),
            )

        #------------------------
        # 2020 Q1~Q4 EPS
        if self.getInfo ("QEPS", "2020Q1", "EPS") != None \
            and self.getInfo ("QEPS", "2020Q2", "EPS") != None \
            and self.getInfo ("QEPS", "2020Q4", "EPS") != None \
            and self.getInfo ("QEPS", "2020Q3", "EPS") != None:
            Q1Q4EPS = self.getInfoFloat ("QEPS", "2020Q1", "EPS") \
                + self.getInfoFloat ("QEPS", "2020Q2", "EPS") \
                + self.getInfoFloat ("QEPS", "2020Q4", "EPS") \
                + self.getInfoFloat ("QEPS", "2020Q3", "EPS")
            self._write (file, res, "2020 Q1~Q4 EPS : %.2f 元", Q1Q4EPS)

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
        # 相關新聞 from yahoo
        self._write (file, res, "[相關新聞]")
        tmp, newsList = StockDBMgr.getNews (self.id)
        for index, news in enumerate (newsList):
            if index >= 10:
                break
            self._write (file, res, "%s %s", news["dateStr"], news["title"])

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
    # 0 : 手工記錄
    # 1 : 2020Q4 公告了
    # 2 : 預估的
    #---------------------------------------
    def _get2020EPS (self):
        # case 0 : 如果有公告 2020Q4，就去抓取
        if self.getInfo ("QEPS", "2020Q4", "EPS") != None and self.getInfo ("QEPS", "2020Q1", "EPS") != None:
            return 0, self.getInfoFloat ("QEPS", "2020Q4", "EPS") + self.getInfoFloat ("QEPS", "2020Q3", "EPS") + self.getInfoFloat ("QEPS", "2020Q2", "EPS") + self.getInfoFloat ("QEPS", "2020Q1", "EPS")
        # case 1 : 如果有公告就以公告為主
        if self.EPS2020 != None:
            return 1, self.EPS2020
        # case 2 : 做預估 2020Q4
        if self.getInfo ("QEPS", "2020Q3", "EPS") != None and self.getInfo ("QEPS", "2020Q2", "EPS") != None and self.getInfo ("QEPS", "2020Q1", "EPS") != None:
            eps2020 = self.getInfoFloat ("QEPS", "2020Q3", "EPS") * 2 \
                    + self.getInfoFloat ("QEPS", "2020Q2", "EPS") \
                    + self.getInfoFloat ("QEPS", "2020Q1", "EPS")
            return 2, eps2020
        # case 3 : 沒有辨法處理
        else:
            return 3, None
    
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
                out_total += self.getInfo ("三大法人")[index]["out"]
                in_total += self.getInfo ("三大法人")[index]["credit"]
            else:
                out_total += abs(self.getInfo ("三大法人")[index]["out"])
                in_total += abs(self.getInfo ("三大法人")[index]["credit"])
            #print (out_total, in_total)
        # 回傳平均結果
        return out_total/counter, in_total/counter
    
    #---------------------------------------
    # 取得指定時間的買賣超
    # 2021/4/28 加入買入價格
    #---------------------------------------
    def _getThreeTotal (self, offset):
        # 外資買賣超總額
        out_total = 0
        out_price = 0
        # 投信買賣超總額
        in_total = 0
        in_price = 0
        # 統計指定區間的結果
        for index in range (0, offset):
            realtime = self.getTodayPrice (index)
            # 計算外資
            out_total += self.getInfo ("三大法人")[index]["out"]
            #out_price = 
            # 計算投信
            in_total += self.getInfo ("三大法人")[index]["credit"]
        
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
            out_tmp = self.getInfo ("三大法人")[index]["out"]
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
            in_tmp = self.getInfo ("三大法人")[index]["credit"]
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

    # 建構子
    def __init__(self):
        # 存放所有的股票列表
        self.stockMap = {}
        # 載入每日資料
        cSingleStock.dayKeyList = StockDBMgr.getDayKey()
        # 載入股票
        self.__loadAllStock ()

    # 載入所有股票資訊
    def __loadAllStock (self):
        print ("[cStockMgr][__loadAllStock] start")
        excel = getExcelSheet ("../all_stock.xlsx", "all_stock")
        for row_index in range (1, 5000):
            if excel.getValue (row_index, 0, None) == None:
                print ("\n結束嚕, 共有 " + str(len(self.stockMap)))
                break
            columnList = [
                # 代碼
                ["id", "", str],
                # 名稱
                ["name", "", str],
                # 上巿 / 上櫃
                ["location", "", str],
                # 產業類型
                ["operationType", "", str],
                # 狀態 : 核心、衛星、短期注意
                ["future", "", str],
                # 一年四季的營收類型
                ["QBType", "", str],
                # 手動買入價
                ["buyPrice", 0, float],
                # 手動賣出價
                ["sellPrice", 0, float],
                # 持有價
                ["holdPrice", 0, float],
                # 高點
                ["highPrice", 0, float],
                # 取得一點影響到大盤的點數
                ["pointToAll", 0, float],
                # 雜項
                ["desc", "", str],
            ]
            # 取得相關資料
            single = cSingleStock()
            for index, [keyword, defaultValue, columnType] in enumerate (columnList):
                tmp = excel.getValue (row_index, index, defaultValue, columnType)
                if columnType == str:
                    tmp = tmp.replace ("%", "%%")
                #single[keyword] = tmp
                setattr (single, keyword, tmp)
                #if keyword == "desc" and tmp != "":
                #    print (single.id, single.name, single.desc)
            # 2021 公告的配股配息
            sdList = StockDBMgr.getSD (single.id)
            if len(sdList) > 0 and sdList[0]["years"] == "2021":
                single.sd2021 = sdList[0]["moneyAll"]
                single.sd2021_stock = sdList[0]["stockAll"]
                if sdList[0]["eps"] != None:
                    single.EPS2020 = sdList[0]["eps"]
            else:
                single.sd2021 = None
                single.sd2021_stock = 0
            # 取得資訊
            infoFilename = "../info/%s.txt" % (single.id,)
            #---------
            # 轉三大法人的資料變成 list
            #---------
            # 沒有個人資訊也不做處理
            #print (infoFilename)
            single.netInfo = getFromCache (infoFilename, {})
            # 要處理三大法人, 從 dict 變 list
            single.netInfo["三大法人"] = StockDBMgr.getThree (single.id)
            # 載入每日資料
            single.netInfo["daily"] = StockDBMgr.getDaily (single.id)
            # 記錄起來
            self.stockMap[single.id] = single
    
    # 取得所有的股票列表
    def getAllStock (self, isNeedNetInfo=False):
        res = {}
        for key, value in self.stockMap.items():
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
