import requests
import threading
import queue
import json
import os


def info():
    info = {
        'name': 'file',
        'path': 'SensitiveFileScanner',
        'fullname': 'SWEP SENSITIVE FILE SCANNER',
        'description': 'A simple sensitive file scanner.',
        'parameters': {
            'Url': 'Target URL.',
            'Threads': 'Threads. Default: 10',
            'SensitiveFileDict': '(OPTIOAL) Sensitive file dictionary',
            'Protocol': 'Protocol. Default: http',
            'Timeout': 'Request timeout. Default: 3'
        },
        'author': 'BREACHER security',
        'date': '2019-01-12'
    }
    return info


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
        while self.queue.qsize():
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
        InformationList = info()
        args = InformationList['parameter']
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


def test():
    scanner = Scanner()
    scanner.info()
