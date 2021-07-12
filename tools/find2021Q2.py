import sys
sys.path.append(r"c:\download\ranb_gametowner\python_module")
from utility import *
sys.path.append (r"..\module")
from AllStockMgr import AllStockMgr
from NetStockInfo import NetStockInfo
import json

# 取得所有的股票
allstock = AllStockMgr.getAllStock ()
#stock_list = []
stock_map = {}
for stockID, stock in allstock.items():
    if stock.getInfo ("QEPS", "2021Q1", "季營收") <= 0.01:
        continue
    # 2021/Q2 的營收比 Q1 好的。
    # 先計算2021Q2 的平均營收
    total_2021Q2 = 0
    counter = 0
    for monthIndex in ["2021/04", "2021/05", "2021/06"]:
        if stock.getInfoInt ("月營收", monthIndex, "月營收") == None:
            break
        total_2021Q2 += stock.getInfoInt ("月營收", monthIndex, "月營收")/100000.0
        counter += 1
    avg_2021Q2 = total_2021Q2/counter
    stock.total_2021Q2 = total_2021Q2
    stock.avg_2021Q2 = avg_2021Q2
    avg_2021Q1 = stock.getInfo ("QEPS", "2021Q1", "平均月營收")
    avg_2020Q4 = stock.getInfo ("QEPS", "2020Q4", "平均月營收")
    if avg_2021Q2 < avg_2021Q1*1.03:
        continue
    if avg_2021Q1 < avg_2020Q4:
        continue
    
    #print (stock.name, stock.getInfo ("QEPS", "2021Q1", "季營收"))
    # 以 2021/Q1 估 2021/Q2 的EPS
    money_2021Q1 = stock.getInfoFloat ("QEPS", "2021Q1", "EPS") * stock.getInfoFloat ("股本") / stock.getInfo ("QEPS", "2021Q1", "季營收")
    money_2021Q2 = money_2021Q1 * total_2021Q2
    stock.money_2021Q2 = money_2021Q2
    eps_2021Q2 = money_2021Q2 / stock.getInfoFloat ("股本")

    # 本益比低
    eps_2021 = (stock.getInfoFloat ("QEPS", "2021Q1", "EPS") + eps_2021Q2) * 2
    stock.eps_2021 = eps_2021
    realtime = stock.getTodayPrice ()
    if eps_2021*12.5 < realtime["end_price"]:
        continue

    # 印出資料
    stock.rate = realtime["end_price"]/eps_2021
    print ("\n~~%s (%s) 股本:%.2f 億~~" % (stock.name, stockID, stock.getInfoFloat ("股本")))
    print ("[2021Q2] 總營收:%.2f 億, 平均營收:%.2f 億, 估EPS : %.2f" % (total_2021Q2, avg_2021Q2, eps_2021Q2))
    print ("[2021Q1] 總營收:%.2f 億, 平均營收:%.2f 億, 估EPS : %s" % (stock.getInfo ("QEPS", "2021Q1", "季營收"), avg_2021Q1, stock.getInfo ("QEPS", "2021Q1", "EPS")))
    print ("現價:%s, 2021估EPS:%.2f, 本益比:%.2f"%(realtime["end_price"], eps_2021, stock.rate))
    #stock_list.append (stockID)
    key = eps_2021Q2 / stock.getInfoFloat ("QEPS", "2021Q1", "EPS")
    if key in stock_map:
        print ("error")
        exit_program()
    stock_map[key] = stock
    
file = open ("../find2021Q2.txt", "w", encoding="utf-8")
keyList = [key for key in stock_map.keys()]
keyList.sort (reverse=True)
for key in keyList:
    stock = stock_map[key]
    file.writelines ("[2021Q2] 總營收:%.2f 億, 成長 %.2f\n" % (stock.total_2021Q2, key))
    file.writelines ("[2021] 全年EPS估:%.2f, 本益比: %.2f\n" % (stock.eps_2021, stock.rate))
    stock.dumpInfo (file)
file.close()

print ("\n[total number] %d\n" % (len(stock_map),))

