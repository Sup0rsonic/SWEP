import queue
import threading
import requests
import json


class Scanner():
    def __init__(self):
        self.Url = None
        self.Threads = 10
        self._Counter = 0
        self.UrlList = []
        self.queue = queue.Queue()
        self.ManageListFile = None
        self.Protocol = 'http'
        self.Name = 'Management Page'
        self.Timeout = 3
        pass


    def LoadDict(self):
        if not self.ManageListFile:
            self.ManageListFile = 'ManageList.json'
        try:
            RawManageJson = json.load(open(self.ManageListFile))
            ManageUrlList = RawManageJson['ManageList']
            ManageUrlList = self.RemoveDuplicate(ManageUrlList)
            for Url in ManageUrlList:
                self.queue.put(Url)
            print '[*] Dictionary load completed, Total %s url(s).' %(len(ManageUrlList))
        except Exception, e:
            print '[!] Failed to load dictionary: %s' %(str(e))
            ManageUrlList = None
        return ManageUrlList


    def RemoveDuplicate(self, List):
        NewList = []
        for item in List:
            if item not in NewList:
                NewList.append(item)
        return NewList
        pass


    def GetPage(self, Url):
        try:
            ManageUrl = '%s://%s/%s' %(self.Protocol, self.Url, Url)
            resp = requests.get(ManageUrl, timeout=self.Timeout)
            if resp.status_code == 200 or resp.status_code == 302:
                self.UrlList.append(ManageUrl)
                print '[+] Get management url: %s ,code=%s' %(ManageUrl, int(resp.status_code))
        except Exception, e:
            print '[!] Error getting management URL: %s' %(str(e))
        self._Counter -= 1
        return


    def ScanManagement(self):
        ManageUrlList = self.LoadDict()
        if not ManageUrlList:
            print '[!] Failed to load Management dictionary file, Quitting.'
            return
        while not self.queue.empty():
            try:
                if self.Threads > self._Counter:
                    self._Counter += 1
                    thread = threading.Thread(target=self.GetPage, args=[self.queue.get()])
                    thread.start()
            except KeyboardInterrupt:
                print '[*] Keyboard interrupt, Quitting.'
            except Exception, e:
                print '[!] Failed to get management Url: %s' %(str(e))
        print '[+] Management scan completed.'
        return self.ManageListFile


    def Scan(self):
        ManagementList = self.ScanManagement()
        return ManagementList


    def info(self):
        print '''
        SWEP MANAGEMENT SCANNER
        Author: BREACHER security
        Description: A simple management bruteforcing tool
        
        ARGS                DESCRIPTION
        ====                ===========
        Url                 Target URL. e.g: www.test.com
        Threads             Threads. Default: 10
        Timeout             Timeout. Default: 3
        ManagementListFile  (OPTIONAL) Management page dictionary.
        Protocol            Protocol. Default: http
        '''
