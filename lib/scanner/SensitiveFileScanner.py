import requests
import threading
import queue
import json
import os
import time


def info():
    info = {
        'name': 'file',
        'path': 'SensitiveFileScanner',
        'fullname': 'SWEP SENSITIVE FILE SCANNER',
        'description': 'A extra simple sensitive file scanner.',
        'parameters': {
            'Url': 'Target URL.',
            'Threads': 'Threads. Default: 10',
            'SensitiveFileDict': '(OPTIONAL) Sensitive file dictionary',
            'Mode': '(OPTIONAL) Wordlist mode(json/plain)',
            'Protocol': 'Protocol. Default: http',
            'Timeout': 'Request timeout. Default: 3'
        },
        'author': 'BREACHERS security',
        'date': '2019-02-05'
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
        self.Mode = 'plain'
        self.UrlList = []
        self.TaskList = []
        self.Timeout = 3
        self.Status = False
        self.Path = os.path.dirname(os.path.abspath(__file__))
        return


    def LoadJson(self):
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
            for item in FileList:
                self.Append(item)
            print '[+] File load success, Total %s item(s).' % (self.queue.qsize())
        except Exception, e:
            print '[!] Failed to load dictionary: %s' %(str(e))
            return
        return


    def LoadFileList(self):
        if not os.path.isfile(str(self.SensitiveFileDict)):
            print '[!] Invalid filename, Using default wordlist.'
            self.SensitiveFileDict = '%s/../../WordList/SensitiveFile' %(self.Path)
        for item in open(str(self.SensitiveFileDict)):
            self.Append(item)
        for ext in ['zip', 'rar', '7z']:
            self.Append(self.Url.replace('.', '') + ext)
            self.Append(self.Url.split('.')[-2] + ext)
        return


    def Append(self, item):
        if item not in self.queue.queue:
            self.queue.put(item)


    def GetSensitiveFile(self):
        if self.Mode != 'json':
            self.LoadFileList()
        else:
            self.LoadJson()
        self.Status = True
        checker = threading.Thread(target=self.ThreadChecker)
        checker.setDaemon(True)
        checker.start()
        while True:
            if self.Threads > self._Counter:
                thread = threading.Thread(target=self.GetPage, args=[self.queue.get()])
                thread.start()
                self.TaskList.append(thread)
                if not self.queue.qsize():
                    for item in self.TaskList:
                        item.join()
                    self.Status = False
                    break
        return self.UrlList

        
        
    def GetPage(self, url):
        Url = '%s://%s/%s' % (self.Protocol, self.Url, url)
        try:
            resp = requests.get(Url, timeout=int(self.Timeout))
            if resp.status_code == 302:
                print '[*] 302 Found found at %s.' %(Url)
                self.UrlList.append(Url)
            elif resp.status_code == 403:
                print '[+] 403 forbidden found at %s.' %(Url)
                self.UrlList.append(Url)
            elif resp.status_code == 200:
                print '[+] HTTP 200 OK found at %s' %(Url)
                self.UrlList.append(Url)
            else:
                pass
        except requests.Timeout:
            print '[!] Request timeout at %s' %(Url)
            pass
        except requests.ConnectionError:
            print '[!] Connection failed to %s' %(Url)
            pass
        except Exception, e:
            print '[!] Failed to fetch page: %s' %(str(e))
        return 


    def Scan(self):
        try:
            if not self.Url:
                print '[!] Url not specified.'
                return
            UrlList = self.GetSensitiveFile()
            print '[+] Found %s file:' % (len(UrlList))
            for item in UrlList:
                print '[+] Sensitive file found: %s' %(item)
        except Exception, e:
            print '[!] Failed to get sensitive file: %s' %(str(e))
            self.UrlList = []
        return self.UrlList


    def ThreadChecker(self):
        time.sleep(1)
        while self.Status:
            for item in self.TaskList:
                if not item.isAlive():
                    self.TaskList.remove(item)
        return


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
    scanner.Url = None
    scanner.Scan()
