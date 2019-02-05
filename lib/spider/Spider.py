import requests
import queue
import threading
import bs4
import time
import re


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
            if not self.GetHomepage():
                return
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
                        for item in self.TaskList:
                            item.join()
                        time.sleep(1)
                if not self.Queue.qsize():
                    print '[*] No URL left, synchronizing tasks.'
                    break
        except Exception, e:
            print '[!] Failed to spider site: %s' %(str(e))
        except KeyboardInterrupt:
            print '[*] User stop.'
        self.Status = False
        print '[+] Spider completed.'
        print '[+] Incoming URL list: '
        for item in self.UrlList:
            print ' |    | %s' %(item)
        print '[+] Fetch completed.'
        return self.UrlList


    def GetHomepage(self):
        self.UrlList = []
        try:
            resp = requests.get('%s://%s' %(self.Protocol, self.Url), timeout=self.Timeout)
            UrlList = self.CheckUrlList(resp)
            UrlList.append('%s://%s' % (self.Protocol, self.Url))
            UrlList = self.ListUpdate(UrlList)
        except requests.Timeout:
            print '[!] Timed out fetching homepage.'
        except requests.ConnectionError:
            print '[!] Failed to connect to server.'
        except Exception ,e:
            print '[!] Failed to fetch url: %s' %(str(e))
        else:
            return UrlList
        print '[!] Spider got a error, quitting.'
        return


    def CheckUrlList(self, resp):
        url = re.sub('/([a-zA-Z0-9\-_]+\.[a-zA-Z0-9]+)$', '', resp.url.split('?')[0])
        resp = resp.text
        soup = bs4.BeautifulSoup(resp)
        a = soup.findAll('a')
        taglist = soup.findAll()
        UrlList = []
        NewUrlList = []
        if not taglist:
            return []
        for item in taglist:
            Url = item.get('href')
            if not Url:
                continue
            if '#' in Url:
                Url = Url.split('#')[0]
            if 'mailto:' in Url or 'irc:' in Url:
                continue
            Url = re.sub('javascript:.*', '', Url)
            if self.Url not in Url:
                if not Url.startswith('//') and not Url.startswith('http'):
                    if Url.startswith('/'):
                        UrlList.append('%s://%s%s' %(self.Protocol, self.Url, Url))
                    elif Url.startswith('..'):
                        PageUrl = '%s://' % (self.Protocol)
                        Path = re.sub('http[s]://', '', url).split('/')
                        for i in range(len(re.findall('\.\.\./', Url))):
                            Path.pop()
                            Path.pop()
                        for i in range(len(re.findall('\.\./', Url))):
                            Path.pop()
                        for i in Path:
                            PageUrl += i
                            PageUrl += '/'
                        UrlList.append(PageUrl)
                    else:
                        UrlList.append('%s/%s' %(url, Url))
            else:
                if Url.startswith('http'):
                    UrlList.append(Url)
                if Url.startswith('//'):
                    UrlList.append('%s:%s' %(self.Protocol, Url))
        for item in UrlList:
            item = item.lstrip('%s://' %(self.Protocol))
            NewUrlList.append('%s://%s' %(self.Protocol, item.replace('//', '/')))
        return NewUrlList


    def ListUpdate(self, UrlList): # Update list.
        if not UrlList:
            return
        for item in UrlList:
            if item not in self.UrlList:
                print '[*] Fetched: %s' % (item)
                self.Queue.put(item)
                self.UrlList.append(item)
        return UrlList


    def GetPage(self, Url):
        try:
            if re.findall('\.zip|\.7z|\.rar|\.jpg|\.png|\.ico|\.pp|\.xls|\.sql|\.mdb|\.pdf|\.fl|\.sw|\.tar|\.gif|\.svg|\.exe|\.msi|\.dmg|\.ap|\.pk',Url , re.MULTILINE+re.IGNORECASE):
                print '[W] IGNORING non-page file %s.' %(Url)
                return
            head = requests.head(Url, timeout=self.Timeout)
            if head.status_code == 404:
                print '[W] 404 Not Found at %s' %(Url)
                return
            if 'text' not in head.headers['Content-Type'] or 'application' in head.headers['Content-Type']:
                print '[*] Non-text item %s found, passing.' %(Url)
                return
            resp = requests.get(Url ,timeout=self.Timeout)
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
        while self.Status:
            for item in self.TaskList:
                if not item.isAlive():
                    self.TaskList.remove(item)


def test():
    spider = Spider()
    spider.Thread = 20
    spider.Url = ''
    spider.SpiderSite()
