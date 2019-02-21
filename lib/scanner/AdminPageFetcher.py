import requests
import queue
import threading
import os
import difflib


# Should I make this wheel?
# Maybe, but looks not a good choice.
# Anyway, better then not.


def info():
    info = {
        'name': 'admin',
        'path': 'AdminPageFetcher',
        'fullname': 'SWEP ADMIN PAGE FETCHER',
        'description': 'Better admin page fetcher with code and page ratios.',
        'parameters':{
            'Url': 'Target URL',
            'Protocol': 'Protocol. Default: http',
            'AdminPageDict': 'Admin page dictionary. Default: WordLists/AdminPages',
            'Threads': 'Threads. Default: 10',
            'Timeout': 'Request timeout. Default: 3'
        },
        'author': 'BREACHER security',
        'date': '2019-01-12'
    }
    return info



class Scanner():
    def __init__(self):
        self.Url = None
        self.AdminPageDict = None
        self.Protocol = 'http'
        self.Threads = 10
        self.Timeout = 3
        self.NotFoundPageRatio = 0.9
        self.NotFoundText = None
        self.NotFoundCode = None
        self.Status = False
        self.TaskList = []
        self.AdminPageList = []
        self.Queue = queue.Queue()
        self.Path = os.path.abspath(__file__)
        self.Dir = os.path.dirname(self.Path)
        pass


    def Scan(self):
        if not self.Url:
            print '[!] URL not specified.'
            return
        elif not self.AdminPageDict or not os.path.isfile(self.AdminPageDict):
            print '[*] Admin page list not specified, using default.'
            self.AdminPageDict = '%s/../../WordLists/AdminPages' %(self.Dir)
        elif not self.Threads:
            print '[*] Thread not specifed, using 10 by default.'
            self.Threads = 10
        elif not self.NotFoundPageRatio:
            print '[*] 404 page ratio not specified, using 0.9 by default.'
            self.NotFoundPageRatio = 0.9
        elif not self.Timeout:
            print '[*] Timeout not specified, using 3 by default.'
        self.Threads = int(self.Threads)
        self.Timeout = int(self.Timeout)
        self.NotFoundPageRatio = int(self.NotFoundPageRatio)
        self.AdminPageDict = open(self.AdminPageDict).read().split('\n')
        print '[*] Loaded %i item(s).' %(len(self.AdminPageDict))
        self.GetNotFoundPage()
        checker = threading.Thread(target=self.ThreadChecker)
        checker.setDaemon(True)
        self.Status = True
        for item in self.AdminPageDict:
            self.Queue.put('%s%s' %(self.Url, item))
        checker.start()
        while True:
            if self.Threads > len(self.TaskList):
                thread = threading.Thread(target=self.PageFetcher, args=[self.Queue.get()])
                thread.start()
                self.TaskList.append(thread)
                if self.Queue.qsize() == 0:
                    print '[*] Scan completed, synchronizing threads.'
                    thread.join()
                    self.Status = False
                    break
        print '[+] Scan completed.'
        if len(self.TaskList):
            print '[*] %i item(s) found. '%(len(self.AdminPageList))
            for item in self.AdminPageList:
                print ' |    Fetched: %s' %(item)
            print '[*] Output completed.'
        return self.AdminPageList


    def PageFetcher(self, page):
        try:
            print '[*] Scanning %s.' %(page)
            resp = requests.get(page)
            Differ = difflib.SequenceMatcher()
            Differ.set_seqs(resp.text, self.NotFoundText)
            if not self.NotFoundText:
                if requests.get(page, timeout=self.Timeout).status_code != 404:
                    print '[+] Fetched %s' %(page)
            else:
                if requests.get(page).status_code != self.NotFoundCode and Differ.ratio() < self.NotFoundPageRatio:
                    print '[+] Fetched %s.' %(page)
        except requests.Timeout:
            print '[*] Timed out fetching %s' %(page)
        except requests.ConnectionError:
            print '[*] Error connect to server fetching %s.' %(page)
        except Exception, e:
            print '[*] Failed to fetch page %s: %s' %(page, str(e))
        return


    def ThreadChecker(self):
        while True:
            for item in self.TaskList:
                if not item.isAlive():
                    self.TaskList.remove(item)
                    del item
            if not self.Status:
                break
        return


    def GetNotFoundPage(self):
        print '[*] Fetching 404 Page.'
        self.Url = '%s://%s/' %(self.Protocol, self.Url)
        try:
            resp = requests.get('%s24617823612783612798367821637821' %(self.Url), timeout=self.Timeout)
            if resp.status_code == 200:
                resp = requests.get('%s28361287346218937289ijghd219038721wq' %(self.Url))
                if resp.status_code == 200:
                    resp = requests.get('%s/ARealNotFoundPage' %(self.Url))
                    if resp.status_code == 200:
                        print '[!] Got HTTP 200 OK Response in 3 tries, Code will disabled.'
            if resp.status_code == 200:
                self.NotFoundCode = 123321312
            else:
                self.NotFoundCode = resp.status_code
            self.NotFoundText = resp.text
            print '[*] 404 page fetch completed.'
        except Exception, e:
            print '[!] Failed to fetch page: %s, Ratio will disabled' %(str(e))
            self.NotFoundCode = 200
            self.NotFoundPage = None
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



