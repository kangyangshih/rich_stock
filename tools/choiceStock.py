# DESC : 獨立選股程式
# Date : 2020/12/4

import sys
sys.path.append(r"c:\download\ranb_gametowner\python_module")
from utility import *
sys.path.append (r"..\module")
from AllStockMgr import AllStockMgr
from NetStockInfo import NetStockInfo
import json

# 清除暫存檔
#del_dir ("cache")
#check_dir ("cache")

# 取得所有的股票
allstock = AllStockMgr.getAllStock ()

file = open ("../choice_ignore.txt", "w", encoding="utf-8")
def write (strFormat, *args):
    if strFormat == None:
        strFormat = "None"
    strFormat += "\n"
    if len(args) > 0:
        strFormat = strFormat % args
    print (strFormat)
    file.writelines (strFormat)

res = {
}

# 每隻股票都需要去做計算
for stockID, stock in allstock.items():
    write ("處理 %s (%s)" , stock.name, stock.id)

    #---------------------------
    # 配息的相關要求
    #---------------------------

    # 連三年要有配股配息
    sdList = stock.getInfo ("配股配息")
    # 配股不足3年
    if len(sdList) < 3:
        write ("[失敗] 配股不足三年")
        write (json.dumps (sdList))
        continue

    # 近三年沒有連續配股
    if sdList[0]["所屬年度"] != "2019" and sdList[1]["所屬年度"] != "2018" and sdList[2]["所屬年度"] != "2017":
        write ("[失敗] 沒有連三年配股")
        write (json.dumps (sdList[0]))
        write (json.dumps (sdList[1]))
        write (json.dumps (sdList[2]))
        continue
    
    # 希望配息是愈來愈多的, 至少不要低於前一年的 9成
    tmp = [0, 0, 0]
    for index in range (3):
        tmp[index] += float (sdList[index]["股票股利"]) + float (sdList[index]["現金股利"])
    if tmp[0] < tmp[1]*0.9 or tmp[1] < tmp[2]*0.9:
        write ("[失敗] 沒有愈配愈多")
        write ("2019 : %s %s total:%.2f", sdList[0]["股票股利"], sdList[0]["現金股利"], tmp[0])
        write ("2018 : %s %s total:%.2f", sdList[1]["股票股利"], sdList[1]["現金股利"], tmp[1])
        write ("2017 : %s %s total:%.2f", sdList[2]["股票股利"], sdList[2]["現金股利"], tmp[2])
        continue
    
    #---------------------------
    # 營收相關要求
    #---------------------------
    # 缺營收資料就暫不處理
    if stock.getInfo ("QEPS", "2020Q4", "EPS") == None or \
        stock.getInfo ("QEPS", "2020Q3", "EPS") == None or \
        stock.getInfo ("QEPS", "2020Q2", "EPS") == None or \
        stock.getInfo ("QEPS", "2020Q1", "EPS") == None:
        write ("[失敗] 無法取得 2020 Q1, Q2, Q3 的EPS")
        write (stock.getInfo ("QEPS", "2020Q4", "EPS"))
        write (stock.getInfo ("QEPS", "2020Q3", "EPS"))
        write (stock.getInfo ("QEPS", "2020Q2", "EPS"))
        write (stock.getInfo ("QEPS", "2020Q1", "EPS"))
        continue
    
    # 希望今年前三季賺超過去年
    eps2020Q1Q3 = stock.getInfoFloat ("QEPS", "2020Q3", "EPS") \
            + stock.getInfoFloat ("QEPS", "2020Q2", "EPS") \
            + stock.getInfoFloat ("QEPS", "2020Q1", "EPS")
    if eps2020Q1Q3 < 0:
        write ("[失敗] 2020 前三季EPS為負")
        write (stock.getInfo ("QEPS", "2020Q3", "EPS"))
        write (stock.getInfo ("QEPS", "2020Q2", "EPS"))
        write (stock.getInfo ("QEPS", "2020Q1", "EPS"))
        continue

    eps2019 = stock.getInfoFloat ("QEPS", "2019", "EPS")
    if eps2019 < 0:
        write ("[失敗] 2019 EPS 為負 : %.2f", eps2019)
        continue

    if eps2020Q1Q3 < eps2019 * 0.85:
        write ("[失敗] 2020 賺的比較少一點")
        write ("2020 Q1~Q3 : %.2f", eps2020Q1Q3)
        write ("2019 : %.2f", eps2019)
        continue
    
    # 近3年EPS成長
    eps2018 = stock.getInfoFloat ("QEPS", "2018", "EPS")
    eps2017 = stock.getInfoFloat ("QEPS", "2017", "EPS")
    if eps2019 < eps2018 * 0.95 or eps2018 < eps2017 * 0.95:
        write ("[失敗] 近3年EPS沒有持續成長")
        write ("2019 EPS: %.2f", eps2019)
        write ("2018 EPS: %.2f", eps2018)
        write ("2017 EPS: %.2f", eps2017)
        continue
    
    #---------------------------
    # 過濾掉業外營收太多的
    #---------------------------
    # 2020Q3 EPS:3.78, 毛利率 : 19.46 %, 營業利益率 : 7.38 %, 稅前淨利率:76.01 %
    # 2020Q2 EPS:0.46, 毛利率 : 17.68 %, 營業利益率 : 7.43 %, 稅前淨利率:10.26 %
    keyList = ["2020Q3", "2020Q2", "2020Q1"]
    isIgnore = False
    for index, key in enumerate(keyList):
        tmp0 = stock.getInfoFloat ("QEPS", key, "營業利益率")
        tmp1 = stock.getInfoFloat ("QEPS", key, "稅前淨利率")
        if tmp1 * 0.8 > tmp0:
            write ("[%s] 業外營收太多 稅前淨利率(%.2f) > 營業利益率(%.2f)", key, tmp1, tmp0)
            isIgnore = True
    if isIgnore == True:
        write ("[失敗] 2020 業外營收占比太重")
        continue


    # 加入結果
    res[stockID] = stock

file.close()

print ("合乎目標數量 :", len(res))

file = open ("../choice.txt", "w", encoding="utf-8")
for stockID, stock in res.items():
    stock.dumpInfo (file)
file.close()
