import queue
import threading
import requests
import json
import time

test = 1

def info():
    info = {
        'name': 'manage',
        'path': 'ManagementScanner',
        'fullname': 'SWEP MANAGEMENT PAGE SCANNER',
        'description': 'A simple management bruteforcing tool.',
        'parameters': {
            'Url': 'Target URL',
            'Threads': 'Threads. Default: 10',
            'Timeout': 'Request timeout. Default: 3',
            'ManagementListFile': '(OPTIONAL) Management page dictionary',
            'Protocol': 'Protocol. Default: http'
        },
        'author': 'BREACHER security',
        'date': '2019-01-12'
    }
    return info


class Scanner():
    def __init__(self):
        self.Url = None
        self.Threads = 10
        self.UrlList = []
        self.Queue = queue.Queue()
        self.Time = 0
        self.ManageListFile = None
        self.Protocol = 'http'
        self.Name = 'Management Page'
        self.TaskList = []
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
                self.Queue.put(Url)
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
        return


    def ScanManagement(self):
        ManageUrlList = self.LoadDict()
        if not ManageUrlList:
            print '[!] Failed to load Management dictionary file, Quitting.'
            return
        thread = threading.Thread(target=self.ThreadChecker)
        thread.setDaemon(True)
        self.Status = True
        thread.start()
        while True:
            try:
                if self.Threads > len(self.TaskList):
                    thread = threading.Thread(target=self.GetPage, args=[self.Queue.get()])
                    thread.start() # Fuck race competition. I'm sick of this.
                    self.TaskList.append(thread)
                    if not self.Queue.qsize():
                        print '[*] Scan completed, synchronizing threads.'
                        for item in self.TaskList:
                            item.join()
                        break
            except KeyboardInterrupt:
                print '[*] Keyboard interrupt, Quitting.'
                break
            except Exception, e:
                print '[!] Failed to get management Url: %s' %(str(e))
        print '[+] Management scan completed.'
        self.Status = False
        return self.ManageListFile


    def Scan(self):
        ManagementList = self.ScanManagement()
        return ManagementList


    def ThreadChecker(self):
        time.sleep(1)
        while self.Status:
            for item in self.TaskList:
                if not item.isAlive():
                    self.TaskList.remove(item)
                    del item
        return



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



def test():
    scanner = Scanner()
    scanner.Url = ''
    scanner.Scan()

