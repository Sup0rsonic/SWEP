import requests
import queue
import threading
import difflib
import lib.spider.Spider
import time


def info():
    info = {
        'name': 'xss',
        'path': 'XSSScanner',
        'fullname': 'SWEP XSS SCANNER',
        'description': 'A simple XSS scanner',
        'parameters': {
            'Url': 'Target URL.',
            'Thread': 'Threads. Default: 10',
            'Protocol': '(OPTIONAL) Protocol. Default: http',
            'Timeout': '(OPTIONAL) Request timeout. Default: 3'
        },
        'author': 'BERACHERS security',
        'date': '2019-01-28'
    }
    return info


class Scanner():
    def __init__(self):
        self.Url = None
        self.Protocol = 'http'
        self.Thread = 10
        self.Timeout = 3
        self.TaskList = []
        self.Status = False
        self.VulUrlList = []
        self.PotentialVulUrlList = []
        self.Queue = queue.Queue()
        self.Time = 0
        self.Spider = lib.spider.Spider.Spider()
        pass


    def Scan(self):
        if not self.Url:
            print '[!] URL not specified.'
            return
        elif not self.Protocol:
            print '[!] Protocol not specified, using http.'
            self.Protocol = 'http'
        elif not self.Thread:
            print '[!] Thread not specified, using 10.'
            self.Thread = 10
        elif not self.Timeout:
            print '[!] Timeout not specified, using 3.'
        try:
            Url = '%s://%s/' %(self.Protocol, self.Url)
            self.Thread = int(self.Thread)
            self.Spider.Url = self.Url
            UrlList = self.Spider.SpiderSite()
            if not UrlList:
                print '[!] Failed to spider site.'
                return
            if raw_input('[*] Spider completed. %s items. Do you want to shrink URL list?(Y/n)' %(str(len(UrlList)))):
                UrlList = self.SimplifyPageList(UrlList)
            for item in UrlList:
                self.Queue.put(item)
            self.Status = True
            checker = threading.Thread(target=self.ThreadChecker)
            checker.setDaemon(True)
            timer = threading.Thread(target=self.Timer)
            timer.setDaemon(True)
            statchecker = threading.Thread(target=self.StatChecker)
            timer.setDaemon(True)
            checker.start()
            timer.start()
            statchecker.start()
            while True:
                if len(self.TaskList) < self.Thread:
                    thread = threading.Thread(target=self.CheckXSS, args=[self.Queue.get()])
                    thread.start()
                    self.TaskList.append(thread)
                    if self.Queue.qsize() == 0:
                        thread.join()
                        break
            print '[*] Check completed.'
            VulUrlCount = len(self.VulUrlList)
            PotentialUrl = len(self.PotentialVulUrlList)
            print '[*] %s vulnerable URL found.' %(str(len(self.VulUrlList)))
            if VulUrlCount:
                print '[*] Incoming vulnerable URL.'
                for item in self.VulUrlList:
                    print '[+]  | %s' %(item)
            if PotentialUrl:
                print '[*] Incoming potential vulnerable URL list.'
                for item in self.PotentialVulUrlList:
                    print '[+]  | %s' %(item)
        except Exception, e:
            print '[!] Failed checking XSS: %s '%(str(e))
        print '[+] Check completed.'
        return (self.VulUrlList, self.PotentialVulUrlList)


    def GenList(self, Url):
        try:
            UrlList = []
            if len(Url.split('?')) == 1 or len(Url.split('?')[1].split('=')) == 1:
                return
            RawUrl = ''
            Page, ParmList = Url.split('?') # http://www.test.com/, test=123&test1=123123
            RawUrl += Page
            RawUrl += '?'
            ParmList = ParmList.split('&') # test=123, test1=123123
            for item in ParmList:
                Url = Page
                Url += '?'
                Url += item
                Url += '</TestParm>'
                for parm in ParmList:
                    if item == parm:
                        continue
                    Url += '&'
                    Url += parm
                    UrlList.append(Url)
        except Exception , e:
            print '[!] Failed generating URL: %s' %(str(e))
            return
        return UrlList



    def CheckXSS(self, Url):
            try:
                CheckUrl = self.GenList(Url)
                if not CheckUrl:
                    return
                for item in CheckUrl:
                    RawResp = requests.get(Url, timeout=3).text
                    ChkResp = requests.get(item, timeout=3)
                    print '[*] Checking %s' %(str(item))
                    if ChkResp.status_code == 404:
                        if '</TestParam>' in ChkResp.text:
                            print '[*] %s seems vulnerable but SWEP got a 404 code.' % (item)
                            self.PotentialVulUrlList.append(Url)
                        return
                    if '</TestParam>' in ChkResp.text:
                        print '[+] %s seems vulnerable.' % (Url)
                        self.VulUrlList.append(item)
                    elif 'TestParm' in ChkResp.text:
                        print '[*] %s seems vulnerable but filtered <>/.' % (item)
                        self.PotentialVulUrlList.append(Url)
                    elif '/TestParm' in ChkResp.text:
                        print '[*] %s seems vulnerable but filtered <>.' % (item)
                        self.PotentialVulUrlList.append(Url)
                    else:
                        pass
            except Exception, e:
                print '[!] Failed checking XSS, URL=%s: %s' %(Url, e)
            return



    def SimplifyPageList(self, pagelist): # A counter: time cost here = 0 minutes. Copied from sql injection scanner to save time.
        UrlList = []
        SavedUrl = {}
        for item in pagelist:
            try:
                ArgList = item.split('?')
                if len(ArgList) == 1:
                    continue
                ParmArgList = ArgList[1].split('&')
                ParmArgDict = {}
                for Argument in ParmArgList:
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
            except Exception, e:
                print '[!] Failed to load URL: %s' %(str(e))
        return UrlList



    def SortNew(self, dict): # Copied from sql injection scanner.
        NewList = dict
        NewList.sort()
        return NewList


    def info(self):
        InformationList = info()
        args = InformationList['parameters']
        print '[*] Incoming scanner information:'
        print '[*] Scanner name: %s' %(InformationList['name'])
        print ' |   %s' %(InformationList['fullname'])
        print ' |   Description: %s' %(InformationList['description'])
        print ' |   Author: %s' %(InformationList['author'])
        print ' |   Date: %s' %(InformationList['date'])
        print ' |   Arguments: Total %i' %(len(args))
        print ' |    |  NAME        DESCRIPTION'
        print ' |    |  ----        `-----------'
        for item in args.keys():
            print ' |    |  %s%s' %(item.ljust(12), args[item])
        print ' |'
        print '[*] Scanner information end.'


    def ThreadChecker(self):
        time.sleep(3)
        while True:
            for item in self.TaskList:
                if not item.isAlive():
                    self.TaskList.remove(item)
            if not self.Queue.qsize() and len(self.TaskList) == 0:
                self.Status = False
                break


    def Timer(self):
        while self.Status:
            time.sleep(1)
            self.Time += 1


    def StatChecker(self):
        while self.Status:
            time.sleep(5)
            print '[*] %s thread running, %s item left, cost %s seconds' %(str(len(self.TaskList)), str(self.Queue.qsize()), self.Time)



def test():
    scanner = Scanner()
    scanner.Url = 'www.co-effort.com'
    scanner.Scan()

