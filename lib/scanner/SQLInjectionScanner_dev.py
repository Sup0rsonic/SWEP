import lib.spider.SpiderNew
import lib.spider.Spider
import lib.config
import re
import requests
import difflib
import Queue
import threading
import json
import time
import os
import subprocess


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
            'ParameterMode': 'Parameter mode for pages without parameter, "Manual" or "M" for manual, "Skip" for or "S" to skip. Default: Skip',
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
        self.ParameterMode = 'skip'
        self.Thread = 10
        self.Timeout = 3
        self._Counter = 0
        self.Time = 0
        self.Queue = Queue.Queue()
        self.TaskList = []
        self.Differ = difflib.SequenceMatcher()
        self.path = os.path.abspath(__file__)
        self.dir = os.path.dirname(self.path)
        self.FuzzDict = json.load(open('%s/SQLiFuzzList.json' %(self.dir), 'r'))
        self.FuzzKeyword = self.FuzzDict['keyword']
        self.LoadKeywordParms()
        self.VulUrlList = []
        self.Status = False
        self.Spider = lib.spider.Spider.Spider()



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
        if not UrlList:
            while raw_input('[w] Warning: SWEP got an empty page response. do you want to retry?(y/N) ').upper() != 'N':
                UrlList = self.FetchPageList()
                if UrlList:
                    break
            else:
                print '[+] Check completed, No url found.' # So WTF happend?
                return
        if raw_input('[*] %s pages fetched, Do you want to shrink url list for better speed? (Y/n) ' %(len(UrlList))).upper() != 'N':
                UrlList = self.SimplifyPageList(UrlList)
        self.CheckSQLInjection(UrlList)


    def FetchPageList(self):
        try:
            self.Spider.Url = self.Url
            UrlList = self.Spider.SpiderSite()
        except Exception, e:
            print '[!] Failed to get site pages: %s' %(str(e))
            return
        return UrlList


    def SimplifyPageList(self, pagelist): # A counter: time cost here = 50 minutes.
        UrlList = []
        SuffixList = {}
        SavedUrl = {}
        for item in pagelist: # 'http://www.test.com/123?123=321'
            try:
                ArgList = item.split('?')
                if len(ArgList) == 1:
                    if 'M' in self.ParameterMode.upper():
                        if raw_input('[*] Not parameters found on %s. Do you want to modify it manually?(y/N)').upper() != 'Y':
                            SuffixList[ArgList[0]] = None
                        if raw_input('[*] Please specify Long/Short mode.(Long mode: /dir/page.ext, Short mode: page.ext)(L/s)').upper() != 's':
                            url = re.findall('//.*$', ArgList[0])
                        else:
                            url = re.findall('/[^/]*$', ArgList[0])
                        if url not in SuffixList.keys():
                            while True:
                                parm = raw_input('[*] Parameter(s) for %s. e.g: parm1=123&parm2=321: ' %(url))
                                if '=' in parm:
                                    break
                                if raw_input('[*] Invalid format, Retype?(Y/n)').upper() == 'N':
                                    if raw_input('[*] Do you want to pass this page in remaining test?(y/N) ').upper() != 'Y':
                                        continue
                                    else:
                                        SuffixList[ArgList[0]] = None
                            SuffixList[url] = parm
                        if not SuffixList[ArgList[0]]:
                            continue
                        ArgList.append(SuffixList[url])
                    else:
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
        self.Stat = True
        if not UrlList:
            print '[!] Empty URL list found, quitting.'
            return
        for item in UrlList:
            self.Queue.put(item)
        print '[+] Queue generate completed, Total %i item(s).' %(self.Queue.qsize())
        self.Status = True
        counter = threading.Thread(target=self._ThreadCounter)
        counter.setDaemon(True)
        checker = threading.Thread(target=self._ThreadChecker)
        checker.setDaemon(True)
        counter.start()
        checker.start()
        try:
            while True:
                if not self.Queue.qsize():
                    break
                if len(self.TaskList) < self.Thread:
                    thread = threading.Thread(target=self._SQLInjectionChecker, args=[self.Queue.get()])
                    thread.start()
                    self.TaskList.append(thread)
                    if not self.Queue.qsize():
                        thread.join()
                        break
        except KeyboardInterrupt:
            print '[*] User stop.'
        except Exception, e:
            print '[!] Failed to check SQL injection: %s' %(str(e))
        self.Stat = False
        return


    def _SQLInjectionChecker(self, url):
        UrlList = []
        rawresp = None
        while not rawresp:
            try:
                rawresp = requests.get(url, timeout=int(self.Timeout)).text
            except requests.Timeout:
                print '[!] Timed out feching %s.' %(url)
            except requests.ConnectionError:
                print '[!] Failed to connect to server fetching %s.' %(url)
            except Exception, e:
                print '[!] Failed to fetch page %s: %s' %(url, str(e))
                if raw_input('[*] Do you want to retry?(Y/n)').upper() == 'N':
                    return
                else:
                    continue
            finally:
                if requests.RequestException:
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
        return


    def _ThreadCounter(self):
        while self.Stat:
            time.sleep(5)
            self.Time += 5
            print '[*] Used %i seconds, %i page(s) total, %i vulnerable page(s) found, %i pages left.' %(self.Time,self.Queue.qsize() , len(self.VulUrlList), self.Queue.qsize())


    def _ThreadChecker(self):
        while self.Stat:
            for item in self.TaskList:
                if not item.isAlive():
                    self.TaskList.remove(item)


    def SortNew(self, dict):
        NewList = dict
        NewList.sort()
        return NewList


def test():
    scanner = Scanner()
    scanner.Url = '192.168.0.101:8081/sqli-labs'
    scanner.Scan()
    return


if __name__ == '__main__':
    test()
