import lib.spider.SpiderNew
import lib.spider.Spider
import re
import requests
import difflib
import Queue
import threading
import json
import time


# TEST FEATURE:
# Don't modify this if you didn't read the source.
# May cause depression, physical harm and death.
# SHOULD completed.
# todo: Change mode after development
dev_mode = True


def info():
    info = {
        'name': 'newsql',
        'path': 'SQLInjectionScanner',
        'fullname': 'SWEP SQL INJECTION SCANNER VER2',
        'description': 'A improved simple SQL Injection scanner.',
        'parameters': {
            'Url': 'Target URL.',
            'Thread': 'Threads. Default: 10',
            'Ratio': 'Page difference ratio, Between 0 and 1. Default: 0.8',
            'Protocol': 'Protocol. Default: http',
            'Timeout': 'Request timeout. Default: 3'
        },
        'author': 'BERACHERS security',
        'date': '2019-01-14'
    }
    return info


class Scanner():
    def __init__(self):
        self.Url = None
        self.Ratio = 0.8
        self.Protocol = 'http'
        self.Thread = 10
        self.Timeout = 3
        self._Counter = 0
        self.Timer = 0
        self.Queue = Queue.Queue()
        self.Differ = difflib.SequenceMatcher()
        self.Status = 'None'
        self.FuzzDict = json.load(open('SQLiFuzzList.json'))
        self.FuzzKeyword = self.FuzzDict['keyword']
        self.LoadKeywordParms()
        self.VulUrlList = []
        if dev_mode:
            self.Spider = lib.spider.SpiderNew.Spider()
        else:
            self.Spider = lib.spider.Spider.Spider()
        pass


    def LoadKeywordParms(self):
        self.RespKeyword = ''
        for item in self.FuzzDict:
            self.RespKeyword += item
            self.RespKeyword += '|'
        self.RespKeyword = self.RespKeyword.rstrip('|')
        return


    def Scan(self):
        if not self.Url:
            print '[!] URL not specified.'
        elif not self.Timeout:
            print '[!] Timeout not specified, Using 3 by default.'
            self.Timeout = 3
        elif not self.Ratio:
            print '[!] Ratio not specified, Using 0.8 by default.'
            self.Ratio = 0.8
        elif not self.Protocol:
            print '[!] Protocol not specified, Using http by default.'
            self.Protocol = 'http'
        elif not self.Thread:
            print '[!] Thread not specified, Using 10 by default.'
        UrlList = self.FetchPageList()
        while not UrlList:
            if raw_input('[w] Warning: SWEP got an empty page response. do you want to retry?(y/N) ').upper() != 'Y':
                self.FetchPageList()
            else:
                print '[+] Check completed, No url found.' # So WTF happend?
        if raw_input('[*] %s pages fetched, Do you want to shrink url list for better speed? (Y/n) ').upper() != 'N':
                UrlList = self.SimplifyPageList(UrlList)


    def FetchPageList(self):
        try:
            self.Spider.url = self.Url
            UrlList = self.Spider.SpiderSite()
        except Exception, e:
            print '[!] Failed to get site pages: %s' %(str(e))
            return
        return UrlList


    def SimplifyPageList(self, pagelist): # A counter: time cost here = 50 minutes.
        UrlList = []
        SavedUrl = {}
        for item in pagelist: # 'http://www.test.com/123?123=321'
            try:
                ArgList = item.split('?')
                if len(ArgList) == 1:
                    continue
                ParmArgList = ArgList[1].split('&')
                ParmArgDict = {}
                for Argument in ParmArgList: # Extractval()
                    ArgVal = Argument.split('=')
                    if len(ArgVal) == 1:
                        ArgVal.append('')
                    if ArgVal[0] not in ParmArgDict.keys():
                        ParmArgDict[ArgVal[0]] = ArgVal[1]
                if ArgList[0] not in SavedUrl.keys():
                    SavedUrl[ArgList[0]] = ParmArgDict
                    UrlList.append(str(item))
                else:
                    RawList = self.SortNew(SavedUrl[ArgList[0]].keys())
                    NewList = self.SortNew(ParmArgDict.keys())
                    if RawList != NewList:
                        SavedUrl[ArgList[0]] = ParmArgDict

                        UrlList.append(str(item))
                if dev_mode:
                    print str(SavedUrl)
            except Exception, e:
                print '[!] Failed to load URL: %s' %(str(e))
        return UrlList


    def CheckSQLInjection(self, UrlList):
        if not UrlList:
            print '[!] Empty URL list found.'
        print '[*] Generating Queue.'
        for item in UrlList:
            self.Queue.put(item)
        self.UrlCount = self.Queue.qsize()
        print '[+] Queue generate completed, Total %s item(s).' %(str(self.UrlCount))
        threading.Thread(target=self._Timer, daemon=True).start()
        threading.Thread(target=self._ThreadCounter, daemon=True).start()
        try:
            while self.Queue.qsize() != 0:
                if self._Counter < self.Thread:
                    thread = threading.Thread(target=self._SQLInjectionChecker, args=[self.Queue.get()])
                    thread.start()
                    self._Counter += 1
        except KeyboardInterrupt:
            pass
        except Exception, e:
            pass

    def _SQLInjectionChecker(self, url):
        UrlList = []
        try:
            rawresp = requests.get(url, timeout=int(self.Timeout)).text
        except Exception, e:
            print '[!] Failed to fetch page %s: %s' %(url, str(e))
            self._Counter -= 1
            return
        except requests.Timeout:
            while raw_input('[*] Timeout during fetching raw page %s, retry?(Y/n) ').upper() != 'N':
                rawresp = requests.get(url, timeout=int(self.Timeout)).text
            else:
                print '[*] Timed out fetching url. Quitting.'
                self._Counter -= 1
                return
        try:
            for item in self.FuzzKeyword:
                UrlList.append(url + item)
            for item in UrlList:
                resp = requests.get(item)
                self.Differ.set_seqs(rawresp, resp.text)
                if resp.status_code == 500 or re.findall(self.RespKeyword, resp.text) or self.Differ.ratio() < self.Ratio:
                    print '[+] Potential SQL Injection point found: %s' %(str(url))
                    self.VulUrlList.append(url)
                    break
        except requests.Timeout:
            print '[*] Got a timeout at %s.' %(url)
        except Exception, e:
            print '[!] Failed to fetch a url during fuzzing: %s' %(str(e))
        self._Counter -= 1
        return


    def _Timer(self):
        while True:
            time.sleep(1)
            self.Timer += 1


    def _ThreadCounter(self):
        while True:
            time.sleep(10)
            print '[*] Used %s seconds, %s page(s) total, %s vulnerable page(s) found, %s pages left.' %(str(self.Timer), str(self.UrlCount), str(len(self.VulUrlList)), str(self.Queue.qsize()))



    def SortNew(self, dict):
        NewList = dict
        NewList.sort()
        return NewList


def test():
    scanner = Scanner()
    list = [
        'www.test.com/test/?test=123&test1=1234',
        'www.test.com/test/?test=123&test1=12345',
        'www.test.com/test/?test=123&test1=1234&test2=123321',
        'www.test.com/test/?',
        'www.test.com/test/?qwe',
        'www.test.com/test/?123=321?123=',
        'www.test.com/test/?123.html/123/qwe',
        'www.test.com/test/'
    ]
    print scanner.SimplifyPageList(list)
    return

test()
