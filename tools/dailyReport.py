# DESC : 每天的股票日報
# DATE : 2020/11/23

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
        stockOrder["雜項"][stockID] = stock

file = open("../specialInfo.txt", "w", encoding="utf-8")

def write (strFormat, *args):
    strtmp = (strFormat+"\n") % args
    print (strtmp, end="")
    file.writelines (strtmp)

# 輸出外資連5買、連3買、近3日買超
out_buy_sell_map = {
    # 有三日賣超
    -3:{},
    # 有四日賣超
    -4:{},
    # 有五日賣超
    -5:{},
    # 有三天買超
    3:{},
    # 有四天買超
    4:{},
    # 有五天買超
    5:{},
}

# 輸出投信連5買、連3買、近3日買超
in_buy_sell_map = {
    # 有三日賣超
    -3:{},
    # 有四日賣超
    -4:{},
    # 有五日賣超
    -5:{},
    # 有三天買超
    3:{},
    # 有四天買超
    4:{},
    # 有五天買超
    5:{},
}

for key in priorityKey:
    for stockID, stock in stockOrder[key].items():
        # 取得買賣超
        tmp, num = stock.getOutBuySell ()
        # 取得15日累積
        out_total, in_total = stock._getThreeTotal (15)
        # 計算外本比、投本比
        out_total_rate = stock._getBuyRate (out_total)
        # 處理外資
        if tmp > 0 and out_total_rate < 0.02:
            continue
        # 好了才寫入
        if tmp in out_buy_sell_map:
            out_buy_sell_map[tmp][stock.id] = stock

for key in priorityKey:
    for stockID, stock in stockOrder[key].items():
        # 取得買賣超
        tmp, num = stock.getInBuySell ()
        # 取得15日累積
        out_total, in_total = stock._getThreeTotal (15)
        # 計算外本比、投本比
        in_total_rate = stock._getBuyRate (in_total)
        # 處理外資
        if tmp > 0 and in_total_rate < 0.015:
            continue
        # 好了才寫入
        if tmp in in_buy_sell_map:
            in_buy_sell_map[tmp][stock.id] = stock

# 做輸出的動作
write ("#-------------------------------")
write ("# 外資買超")
write ("#-------------------------------")
for index in (5, 4, 3):
    write ("\n# 外資 %s 日買超清單", index)
    for stockID, stock in out_buy_sell_map[index].items():
        tmp, num = stock.getOutBuySell ()
        # 取得5日累積
        out_tmp, in_tmp = stock._getThreeArg ()
        write ("%s(%s) 今日: %s, 五日累積: %.0f, 平均: %.0f", 
            stock.name, 
            stock.id, 
            stock.getInfo ("三大法人")[0]["out"],
            num,
            out_tmp,
        )
        stock.dumpInfo (file)
    
write ("#-------------------------------")
write ("# 外資賣超")
write ("#-------------------------------")
for index in (-5, -4, -3):
    write ("\n# 外資 %s 日買超清單", index)
    for stockID, stock in out_buy_sell_map[index].items():
        tmp, num = stock.getOutBuySell ()
        out_tmp, in_tmp = stock._getThreeArg ()
        #today_out = float(self.getInfo ("三大法人")[0]["out"].replace(",", ""))
        write ("%s(%s) 今日: %s, 五日累積: %.0f, 平均: %.0f", 
            stock.name, 
            stock.id, 
            stock.getInfo ("三大法人")[0]["out"],
            num,
            out_tmp,
        )
        stock.dumpInfo (file)

write ("#-------------------------------")
write ("# 投信買超")
write ("#-------------------------------")
for index in (5, 4, 3):
    write ("\n# 投信 %s 日買超清單", index)
    for stockID, stock in in_buy_sell_map[index].items():
        tmp, num = stock.getInBuySell ()
        # 取得5日累積
        out_tmp, in_tmp = stock._getThreeArg ()
        write ("%s(%s) 今日: %s, 五日累積: %.0f, 平均: %.0f", 
            stock.name, 
            stock.id, 
            stock.getInfo ("三大法人")[0]["in"],
            num,
            in_tmp,
        )
        stock.dumpInfo (file)
    
write ("#-------------------------------")
write ("# 投信賣超")
write ("#-------------------------------")
for index in (-5, -4, -3):
    write ("\n# 投信 %s 日買超清單", index)
    for stockID, stock in in_buy_sell_map[index].items():
        tmp, num = stock.getInBuySell ()
        out_tmp, in_tmp = stock._getThreeArg ()
        write ("%s(%s) 今日: %s, 五日累積: %.0f, 平均: %.0f", 
            stock.name, 
            stock.id, 
            stock.getInfo ("三大法人")[0]["in"],
            num,
            in_tmp,
        )
        stock.dumpInfo (file)

# 輸出殖利率的排行榜

# 每日個股資訊
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