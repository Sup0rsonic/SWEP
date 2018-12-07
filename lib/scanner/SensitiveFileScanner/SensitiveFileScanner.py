import requests
import threading
import queue
import json
import os


class Scanner():
    def __init__(self):
        self.Url = None
        self.SensitiveFileDict= None
        self.Threads = 10
        self._Counter = None
        self.queue = queue.Queue()
        self.Protocol = 'http'
        self.UrlList = []
        self.Timeout = 3
        self.Name = 'SensitiveFile'
        self.Path = os.path.dirname(os.path.abspath(__file__))
        return


    def LoadFileList(self):
        try:
            if not self.SensitiveFileDict:
                print '[*] Dictionary not specified, Using default.'
                self.SensitiveFileDict = '%s/SensitiveFileList.json' %(self.Path)
            try:
                RawJson = json.load(open(self.SensitiveFileDict))
                FileList = RawJson['file']
            except Exception, e:
                print '[!] Failed to load sensitive file: %s' %(str(e))
                return
            if not FileList:
                return
            NewList = []
            for item in FileList:
                if item not in NewList:
                    NewList.append(item)
                    self.queue.put(item)
            print '[+] File load success, Total %s item(s).' % (str(len(NewList)))
        except Exception, e:
            print '[!] Failed to load dictionary: %s' %(str(e))
            return
        return NewList




    def GetSensitiveFile(self):
        FileList = self.LoadFileList()
        while not self.queue.empty():
            if self.Threads > self._Counter:
                thread = threading.Thread(target=self.GetPage, args=[self.queue.get()])
                thread.start()
        return self.UrlList
        
        
    def GetPage(self, url):
        try:
            if requests.get('%s://%s/%s' %(self.Protocol, self.Url, url), timeout=3).status_code != 404:
                self.UrlList.append(url)
                print '[+] Sensitive file found at: %s' %('%s://%s/%s' %(self.Protocol, self.Url ,url))
        except requests.Timeout:
            pass
        except requests.ConnectionError:
            pass
        except Exception, e:
            print '[!] Failed to fetch page: %s' %(str(e))
        return 


    def Scan(self):
        try:
            if not self.Url:
                print '[!] Url not specified.'
            UrlList = self.GetSensitiveFile()
            print '[+] Found %s file:' % (len(UrlList))
            for item in UrlList:
                print '[+] Sensitive file found: %s' %(item)
        except Exception, e:
            print '[!] Failed to get sensitive file: %s' %(str(e))
            self.UrlList = None
        return self.UrlList


    def info(self):
        print """
        SWEP SENSITIVE FILE SCANNER
        Author: BREACHER security
        Description: A simple sensitive file scanner.
        
        ARGS                DESCRIPTION
        ====                ===========
        Url                 Target URL. e.g: www.test.com
        Threads             Threads. Default: 10
        SensitiveFileDict   (OPTIONAL) Sensitive file dictionary. Default: SensitiveFileDict.json
        Protocol            Protocol. Default:http
        Timeout             (OPTIONAL) Timeout. Default: 3
        """


def test():
    scanner = Scanner()
    scanner.Url = 'www.test.com'
    scanner.Scan()

