import requests
import bs4
import re
import queue
import threading
import time


class Spider():
    def __init__(self):
        self.Url = None
        self.Protocol = 'http'
        self.Thread = 10
        self.UrlList = []
        self.Timeout = 1
        self.Queue = queue.Queue()
        self._Counter = 0
        self._ConnErrorCounter = 0
        self._Time = 0
        pass


    def FetchHomepage(self):
        try:
            resp = requests.get(str('%s://%s' %(self.Protocol, str(self.Url)))).text
            InitalPages = self.GetLink(resp)
            print '[+] Fetched %s page from homepage.' %(len(InitalPages))
            return InitalPages
        except Exception, e:
            print '[!] Failed to get homepage: %s' %(str(e))
        return None


    def GetLink(self, page):
        UrlList = []
        soup = bs4.BeautifulSoup(page)
        a = soup.findAll('a')
        for item in a:
            link = re.findall('href=\"(.*?)\"', str(item))
            if not link:
                continue
            link = link[0]
            if 'http' not in link:
                if '//' not in link:
                    pass
            elif self.Url in link:
                pass
            else:
                continue
            if item not in UrlList:
                UrlList.append(link)
        return UrlList


    def Getpage(self, page):
        try:
            resp = requests.get(page, timeout=int(self.Timeout)).text
            self.CheckDuplicate(self.GetLink(resp))
        except requests.ConnectionError:
            print '[!] Request get a connection error.'
            self._ConnErrorCounter += 1
        except requests.Timeout:
            print '[!] Request timeout at %s' %(page)
        self._Counter -= 1
        return


    def CheckDuplicate(self, UrlList):
        NewUrl = []
        for item in UrlList:
            if self.Url not in item:
                if '//' not in item: # '/test/123'
                    item = '%s://%s/%s' %(self.Protocol, self.Url, item)
            elif not re.findall('^http', item): # '//test.test/test/123'
                item = '%s:%s' %(self.Protocol, item)
            else: # 'http://test.test/test/123'
                 pass
            if item not in self.UrlList:
                self.UrlList.append(str(item))
                NewUrl.append(item)
                self.Queue.put(item)
                print '[+] Fetched page: %s' %(str(item))
        return NewUrl


    def SpiderSite(self):
        try:
            if not self.Url:
                print '[!] Error: URL not found.'
            elif not self.Protocol:
                print '[!] Error: No protocol, using HTTP.'
                self.Protocol = 'http'
            elif not self.Timeout:
                print '[!] Error: No timeout, using 3 second(s).'
                self.Timeout = 3
            HomepageList = self.FetchHomepage()
            if not HomepageList:
                print '[!] Failed fetching homepage.'
                return
            UrlList = self.CheckDuplicate(HomepageList)
            CountThread = threading.Thread(target=self.ThreadCounter)
            CountThread.setDaemon(True)
            Timer = threading.Thread(target=self.Timer)
            Timer.setDaemon(True)
            CountThread.start()
            Timer.start()
            while self.Queue.qsize():
                if self.Thread > self._Counter:
                    threading.Thread(target=self.Getpage, args=(self.Queue.get(), )).start()
                    self._Counter += 1
            print '[+] Spider completed, total %s page(s) fetched in %s second(s).' %(str(len(self.UrlList)), str(self._Time))
        except KeyboardInterrupt:
            print '[*] Spider stop, total %s page(s) fetched in %s second(s).' %(str(len(self.UrlList)), str(self._Time))
        except Exception, e:
            print '[*] Spider got an error, total %s page(s) fetched in %s second(s)' %(str(len(self.UrlList)), str(self._Time))
            print '[!] Failed to spider site: %s' %(str(e))
        return self.UrlList


    def ThreadCounter(self):
        while True:
            time.sleep(3)
            print '[*] Current thread: %s, %s page(s) left.' %(str(self._Counter), str(self.Queue.qsize()))
        pass


    def Timer(self):
        while True:
            time.sleep(1)
            self._Time += 1
        pass


def test():
    spider = Spider()
    spider.Url = 'www.phpcms.cn'
    spider.SpiderSite()
