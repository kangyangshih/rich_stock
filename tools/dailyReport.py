# DESC : 每天的股票日報
# DATE : 2020/11/23
# dailyReport.py del

import sys
sys.path.append(r"c:\download\ranb_gametowner\python_module")
from utility import *
sys.path.append (r"..\module")
from AllStockMgr import AllStockMgr
from NetStockInfo import NetStockInfo
import json

# 清除暫存檔
if len(sys.argv) > 1:
    del_dir ("cache")
    check_dir ("cache")

# 取得所有的股票
allstock = AllStockMgr.getAllStock ()
priorityKey = [
    "持有",
    "核心", 
    "衛星",
    "定存", 
    "短期注意",
    "當沖空",
    "電腦選",
    "阮老師",
    "老師選",
    "導線架",
    "太陽能", 
    "風電",
    "DRAM",
    "遊戲",
    "鑽針",
    "通路",
    "台積電", 
    "聯電",
    "鴻海",
    "華為",
    "矽晶圓",
    "Apple",
    "被動元件", 
    "工具機",
    "聯發科",
    "散熱",
    "PCB", 
    "Tesla",
    "Mini-LED",
    "PC",
    "電信",
    "面板",
    "封測廠", 
    "口罩",
    "手套",
    "自行車",
    "汽車",
    "車用",
    "資產",
    "健身器材",
    "紡織",
    "通路",
    "電源供應器",
    "資料中心",
    "光學鏡頭廠",
    "生醫股",
    "金融股",
    "電機機械",
    "營建",
    "雜項",
]

stockOrder = {}
for key in priorityKey:
    stockOrder[key] = {}

for stockID, stock in allstock.items():
    # 特別處理持有型股票
    if stock.holdPrice != 0:
        stockOrder["持有"][stockID] = stock
        # 就重覆寫沒關係
        #continue
    # 如果有在裏面, 就依照順序
    isOrder = False
    for key, value in stockOrder.items():
        # 換個判定寫法
        #if stock.operationType == key:
        if stock.future.find (key) != -1:
            value[stockID] = stock
            isOrder = True
            # 就重覆寫沒關係
            #break
        if stock.operationType.find (key) != -1:
            value[stockID] = stock
            isOrder = True
            # 就重覆寫沒關係
            #break
    # 如果沒在裏面就放在最後
    if isOrder == False and stock.operationType != "":
    #if isOrder == False:
        stockOrder["雜項"][stockID] = stock

file = open ("../price.txt", "w", encoding="utf-8")

def write (strFormat, *args):
    strtmp = (strFormat+"\n") % args
    print (strtmp, end="")
    file.writelines (strtmp)

#----------------------------------------------
# 買入價/放空價的調整
#----------------------------------------------
modify_list = []
for stockID, stock in allstock.items():
    if stock.holdPrice != 0:
        modify_list.append (stockID)
        continue
    if stock.buyPrice != 0:
        modify_list.append (stockID)
        continue
    if stock.emptyPrice != 0:
        modify_list.append (stockID)
        continue
    
for stockID in modify_list:
    allstock[stockID].dumpInfo (file)

file.close()
file = open("../specialInfo.txt", "w", encoding="utf-8")

#----------------------------------------------
# 輸出過去五日外本比、投本比買超前五名
#----------------------------------------------
def getRangeTotalRate (day):
    out_total_map = {}
    in_total_map = {}
    total_total_map = {}
    for stockID, stock in allstock.items():
        # 取得 5 日累積
        out_total, in_total = stock._getThreeTotal (day)
        # 取得 5 日的外本比
        out_total_rate = stock._getBuyRate (out_total)
        if out_total_rate > 0.01:
            if out_total_rate not in out_total_map:
                out_total_map[out_total_rate] = []
            out_total_map[out_total_rate].append (stockID)
        # 取得 5 日的投本比
        in_total_rate = stock._getBuyRate (in_total)
        if in_total_rate > 0.01:
            if in_total_rate not in in_total_map:
                in_total_map[in_total_rate] = []
            in_total_map[in_total_rate].append (stockID)
        # 取得 5 日的總合比
        all_total_rate = stock._getBuyRate (out_total + in_total)
        if all_total_rate > 0.01:
            if all_total_rate not in total_total_map:
                total_total_map[all_total_rate] = []
            total_total_map[all_total_rate].append (stockID)
    return out_total_map, in_total_map, total_total_map

# 做輸出的動作
def printTotalRate (title, header, tmpMap, num=10):
    write ("#-------------------------------")
    write (title)
    write ("#-------------------------------")
    keyList = [value for value in tmpMap.keys()]
    keyList.sort (reverse=True)
    keyList = keyList[:num]
    for key in keyList:
        for stockID in tmpMap[key]:
            write ("%s : %.4f" % ( header, key))
            allstock[stockID].dumpInfo(file)

for day in (5, 30, 10, 15):
    out_total_map, in_total_map, total_total_map = getRangeTotalRate (day)
    #printTotalRate ("外資累計 %s 日買超排行榜" % (day,), "外資累計 %s 日買超" % (day,), out_total_map)
    #printTotalRate ("投信累計 %s 日買超排行榜" % (day,), "投信累計 %s 日買超" % (day,), in_total_map)
    printTotalRate ("外資+投信累計 %s 日買超排行榜" % (day,), "外資+投信累計 %s 日買超" % (day,), total_total_map, 15)

#----------------------------------------------
# 輸出外資/投信合買
#----------------------------------------------
out_in_buy_sell_map = {
    10:{},
    9:{},
    8:{},
    -10:{},
    -9:{},
    -8:{},
}
for stockID, stock in allstock.items():
    # 取得買賣超
    out_day, out_num = stock.getOutBuySell ()
    # 取得15日累積
    out_total, in_total = stock._getThreeTotal (15)
    # 計算外本比、投本比
    out_total_rate = stock._getBuyRate (out_total)
    # 處理外資
    if out_num > 0 and out_total_rate < 0.01:
        continue
    # 取得買賣超
    in_day, in_num = stock.getInBuySell ()
    # 計算外本比、投本比
    in_total_rate = stock._getBuyRate (in_total)
    # 記錄下來
    total_day = in_day + out_day
    if total_day in out_in_buy_sell_map:
        out_in_buy_sell_map[total_day][stockID] = stock

# 做輸出的動作
write ("#-------------------------------")
write ("# 外資/投信買超")
write ("#-------------------------------")
for index in (10, 9, 8, -10, -9, -8):
    write ("\n# 外資/投信 %s 日買超清單", index)
    for stockID, stock in out_in_buy_sell_map[index].items():
        tmp, num = stock.getOutBuySell ()
        # 取得5日累積
        out_tmp, in_tmp = stock._getThreeArg ()
        write ("%s(%s) 外資 今日: %s, 五日累積: %.0f, 平均: %.0f", 
            stock.name, 
            stock.id, 
            stock.getInfo ("三大法人")[0]["out"],
            num,
            out_tmp,
        )
        tmp, num = stock.getInBuySell ()
        # 取得5日累積
        out_tmp, in_tmp = stock._getThreeArg ()
        write ("%s(%s) 投信 今日: %s, 五日累積: %.0f, 平均: %.0f", 
            stock.name, 
            stock.id, 
            stock.getInfo ("三大法人")[0]["in"],
            num,
            in_tmp,
        )
        stock.dumpInfo (file)

#----------------------------------------------
# 每日個股資訊
#----------------------------------------------
file.close()
file = open("../daily.txt", "w", encoding="utf-8")
# 依照重要性來做處理
for key in priorityKey:
    write ("#-------------------------------")
    write ("# %s", key)
    write ("#-------------------------------")
    # 一隻一隻去抓資料處理
    for stockID, stock in stockOrder[key].items():
        # 把資料 dump 下來
        stock.dumpInfo (file)
        # 暫時只先抓一隻
        #break
    # 暫時只抓持有的
    #break

file.close()