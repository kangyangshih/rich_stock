# DESC : 從 Yahoo 抓取及時股價
import sys
sys.path.append(r"c:\download\ranb_gametowner\python_module")
from utility import *
from WebViewMgr import WebViewMgr
import requests
import time
from bs4 import BeautifulSoup
from lxml import etree

class cRealTimeMgr:
    
    def __init__(self):
        self.stockURL = "https://tw.stock.yahoo.com/q/q?s="

    def _get_TAIEX (self):
        WebViewMgr.loadURL (self.allURL)

RealTimeMgr = cRealTimeMgr()

