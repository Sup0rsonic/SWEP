import requests
import queue
import threading
import bs4
import time


# Hope this work. No more bugs. God bless me. Ramen.
# Hope this work. No more bugs. God bless me. Ramen.
# Hope this work. No more bugs. God bless me. Ramen.


debug = True


class Spider():
    def __init__(self):
        self.Url = None
        self.Protocol = 'http'
        self.Thread = 10
        self.Timeout = 3
        self.Queue = queue.Queue()
        self.Status = False
        self.TaskList = []
        self.DuplicateUrl = []
        self.UrlList = []
        self.Time = 0
        pass


    def SpiderSite(self):
        try:
            if not self.Url:
                print '[!] URL not spcified.'
                return
            if not self.Protocol:
                print '[!] Protocol not specified, using HTTP by default.'
                self.Protocol = 'http'
            if not self.Thread:
                self.Thread = 10
            if not self.Timeout:
                self.Timeout = 3
            self.GetHomepage()
            time.sleep(1)
            watcher = threading.Thread(target=self.ThreadWatcher)
            watcher.setDaemon(True)
            timer = threading.Thread(target=self.Timer)
            timer.setDaemon(True)
            watchdog = threading.Thread(target=self.Watchdog)
            watchdog.setDaemon(True)
            self.Status = True
            timer.start()
            watcher.start()
            watchdog.start()
            while True:
                if int(self.Thread) > len(self.TaskList):
                    Url = self.Queue.get()
                    thread = threading.Thread(target=self.GetPage, args=[Url])
                    thread.start()
                    self.TaskList.append(thread)
                    if not self.Queue.qsize():
                        thread.join()
                    if not self.Queue.qsize():
                        print '[*] No URL left, synchronizing tasks.'
                        time.sleep(3)
                if not self.Status:
                    break
        except Exception, e:
            print '[!] Failed to spider site: %s' %(str(e))
        except KeyboardInterrupt:
            print '[*] User stop.'
        print '[+] Spider completed.'
        print '[+] Incoming URL list: '
        for item in self.UrlList:
            print ' |    | %s' %(item)
        print '[+] Fetch completed.'
        return self.UrlList


    def GetHomepage(self):
        try:
            resp = requests.get('%s://%s/' %(self.Protocol, self.Url), timeout=self.Timeout).text
            UrlList = self.CheckUrlList(resp)
            UrlList = self.ListUpdate(UrlList)
        except requests.Timeout:
            print '[!] Timed out fetching homepage.'
        except requests.ConnectionError:
            print '[!] Failed to connect to server.'
        except Exception ,e:
            print '[!] Failed to fetch url: %s' %(str(e))
        return


    def CheckUrlList(self, text):
        soup = bs4.BeautifulSoup(text)
        a = soup.findAll('a')
        UrlList = []
        if not a:
            return
        for item in a:
            Url = item.get('href')
            if not Url:
                continue
            if self.Url not in Url:
                if not Url.startswith('http'):
                    if not Url.startswith('//'):
                        UrlList.append('%s://%s/%s' %(self.Protocol, self.Url, Url))
            else:
                if Url.startswith('http'):
                    UrlList.append(Url)
                if Url.startswith('//'):
                    UrlList.append('%s:%s' %(self.Protocol, Url))
        return UrlList


    def ListUpdate(self, UrlList): # Update list.
        for item in UrlList:
            if item not in self.UrlList:
                print '[*] Fetched: %s' % (item)
                self.Queue.put(item)
                self.UrlList.append(item)
        return UrlList


    def GetPage(self, Url):
        try:
            resp = requests.get(Url ,timeout=self.Timeout).text
            UrlList = self.CheckUrlList(resp)
            self.ListUpdate(UrlList)
        except requests.Timeout:
            print '[!] Request timeout fetching %s' %(Url)
        except requests.ConnectionError:
            print '[!] Failed to connect to server.'
        except Exception, e:
            print '[!] Failed to fetch a url: %s' %(str(e))
        return


    def ThreadWatcher(self):
        while self.Status:
            time.sleep(5)
            print '[*] Thread(s): %s, %s page(s) left, costs %s second(s).' %(len(self.TaskList), self.Queue.qsize(), self.Time)
        return


    def Timer(self):
        while self.Status:
            time.sleep(1)
            self.Time += 1
        return


    def Watchdog(self):
        time.sleep(1)
        while True:
            if len(self.TaskList) == 0 and self.Queue.qsize() == 0:
                self.Status = False
                break
            for item in self.TaskList:
                if not item.isAlive():
                    self.TaskList.remove(item)


def test():
    spider = Spider()
    spider.Url = 'www.jtceramic.com'
    spider.SpiderSite()

