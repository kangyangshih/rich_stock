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
    
    # 做 run 的動作
    def exceute (self, command):
        self._cur.execute (command)

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
    
    # 做檢查的動作
    def __checkInfo (self, tableName, keyMap, isLog=True):
        # 串接出條件
        condition = self.__getMapCondition (keyMap)
        # 串起來資料
        command = "select * from %s where %s;" % (tableName, condition)
        if isLog == True:
            print ("[__checkInfo][command] " + command)
        # 做查詢的動作
        rows = self._cur.execute (command).fetchall()
        if isLog == True:
            print ("[__checkInfo][result] counter:" + str(len(rows)))
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
        print ("[__insert][command] " + command)
        # 做新增的動作
        self.exceute (command)
    
    # 做更新資料的動作
    def __update (self, tableName, infoMap, keyMap):
        # 串接出條件
        condition = self.__getMapCondition (keyMap)
        # 把 infoMap 轉成更新
        res = ""
        for key, value in infoMap.items():
            if isinstance (value, str) == True:
                res += ", %s='%s'" % (key, value)
            else:
                res += ", %s=%s" % (key, value)
        res = res[2:]
        # 串出字串
        command = "update %s set %s where %s;" % (tableName, res, condition)
        print ("[__update][command] " + command)
        # 做更新的動作
        self.exceute (command)

    #-------------------------------------------------------
    # 給外部做使用的 API
    #-------------------------------------------------------
    #-------------------------------------------------------
    # 做更新資料
    def update (self, tableName, infoMap, keyMap):
        # 檢查不是有資料
        res = self.__checkInfo (tableName, keyMap)
        # 有資料 -> 做 update
        if res == True:
            #print ("有資料 -> 做 update")
            self.__update (tableName, infoMap, keyMap)
        # 沒資料 -> 做 insert
        else:
            #print ("沒資料 -> 做 insert")
            self.__insert (tableName, infoMap, keyMap)

    #-------------------------------------------------------
    # 做新增的動作
    def insert (self, tableName, infoMap, keyMap):
        # 檢查不是有資料
        res = self.__checkInfo (tableName, keyMap, False)
        # 有資料 -> 做 update
        if res == False:
            return
        # 沒資料 -> 做 insert
        else:
            #print ("沒資料 -> 做 insert")
            self.__insert (tableName, infoMap, keyMap)

    #-------------------------------------------------------
    # 做刪除的動作
    def delInfo (self, tableName, keyMap):
        pass
