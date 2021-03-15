# DESC : 用來處理 Sqlite 處理
# DATE : 2021/3/11

import sys
sys.path.append(r"c:\download\ranb_gametowner\python_module")
from utility import *
from excel_utility import *
import sqlite3

class cSqlite:
    
    # 初使化的動作
    def __init__(self, name):
        # 資料庫開啟名稱
        self._sqliteName = name
        # 資料庫實體
        self._db = sqlite3.connect (self._sqliteName)
        # 操作體
        self._cur = self._db.cursor ()
    
    # 做關閉的動作
    def __del__(self):
        print ("[cSqlite] del")
        self._db.close()
    
    def close(self):
        self._db.close()
    
    # 做處理的動作
    def commit (self):
        self._db.commit()
    
    # 把 map 轉成字串
    def __getMapCondition (self, keyMap):
        # 串接出條件
        condition = ""
        for key, value in keyMap.items():
            if isinstance (value, str) == True:
                condition += " and %s='%s'" % (key, value)
            else:
                condition += " and %s=%s" % (key, value)
        condition = condition[5:]
        return condition
    
    def __getKeyMap (self, keyMap):
        res = ""
        for key, value in keyMap.items():
            if isinstance (value, str) == True:
                res += ", %s='%s'" % (key, value)
            else:
                res += ", %s=%s" % (key, value)
        res = res[2:]
        return res
    
    def __getFieldList (self, fieldList):
        return ",".join (fieldList)

    # 做檢查的動作
    def checkInfo (self, tableName, keyMap, isLog=True):
        # 串接出條件
        condition = self.__getMapCondition (keyMap)
        # 串起來資料
        command = "select * from %s where %s;" % (tableName, condition)
        if isLog == True:
            #print ("[checkInfo][command] " + command)
            pass
        # 做查詢的動作
        rows = self._cur.execute (command).fetchall()
        if isLog == True:
            #print ("[checkInfo][result] counter:" + str(len(rows)))
            pass
        if len(rows) == 0:
            return False
        else:
            return True

    # 做塞進 DB 的動作
    def __insert (self, talbeName, infoMap, keyMap):
        tmp = {}
        tmp.update (infoMap)
        tmp.update (keyMap)
        # 把 infoMap 轉成更新
        fieldStr = ""
        valueStr = ""
        for key, value in tmp.items():
            if isinstance (value, str) == True:
                fieldStr += ", %s" % (key,)
                valueStr += ", '%s'" % (value,)
            else:
                fieldStr += ", %s" % (key,)
                valueStr += ", %s" % (value,)
        fieldStr = fieldStr[1:]
        valueStr = valueStr[1:]
        # 串出字串
        command = "insert into %s (%s) values (%s);" % (talbeName, fieldStr, valueStr)
        #print ("[__insert][command] " + command)
        # 做新增的動作
        self._cur.execute (command)
    
    # 做更新資料的動作
    def __update (self, tableName, infoMap, keyMap):
        # 串接出條件
        condition = self.__getMapCondition (keyMap)
        # 把 infoMap 轉成更新
        res = self.__getKeyMap (infoMap)
        # 串出字串
        command = "update %s set %s where %s;" % (tableName, res, condition)
        #print ("[__update][command] " + command)
        # 做更新的動作
        self._cur.execute (command)

    #-------------------------------------------------------
    # 給外部做使用的 API
    #-------------------------------------------------------
    #-------------------------------------------------------
    # 做更新資料
    def update (self, tableName, infoMap, keyMap, isUpdate=True):
        # 檢查不是有資料
        res = self.checkInfo (tableName, keyMap)
        # 沒資料 -> 做 insert
        if res == False:
            #print ("沒資料 -> 做 insert")
            self.__insert (tableName, infoMap, keyMap)
        # 有資料 -> 做 update
        elif isUpdate == True:
            #print ("有資料 -> 做 update")
            self.__update (tableName, infoMap, keyMap)
        else:
            pass

    #-------------------------------------------------------
    # 做新增的動作
    def insert (self, tableName, infoMap, keyMap):
        # 檢查不是有資料
        res = self.checkInfo (tableName, keyMap, False)
        # 有資料 -> 做 update
        if res == False:
            return
        # 沒資料 -> 做 insert
        else:
            #print ("沒資料 -> 做 insert")
            self.__insert (tableName, infoMap, keyMap)

    #-------------------------------------------------------
    # 做取得的動作
    def get (self, tableName, fieldList, keyMap, orderStr=""):
        # 串出指令
        command = "select %s from %s where %s" % (
            self.__getFieldList(fieldList), 
            tableName, 
            self.__getKeyMap(keyMap)
        )
        if orderStr != "":
            command = "%s order by %s" % (command, orderStr)
        # 取得結果
        res = []
        rows = self._cur.execute (command).fetchall()
        for row in rows:
            tmp = {}
            for index in range(len(fieldList)):
                tmp[fieldList[index]] = row[index]
            res.append (tmp)
        return res
    
    def getFieldList (self, tableName, fieldName, keyMap, orderStr):
        # select date from daily where id = 1101 group by date order by date desc
        command = "select %s from %s where %s group by %s order by %s" % (
            fieldName,
            tableName,
            self.__getKeyMap(keyMap),
            fieldName,
            orderStr,
        )
        print ("[command]", command)
        res = []
        rows = self._cur.execute (command).fetchall()
        for row in rows:
            res.append (row[0])
        return res

