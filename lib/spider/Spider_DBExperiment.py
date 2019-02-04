import requests
import queue
import threading
import bs4
import time
import re
import sqlite3


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
        self.Database = sqlite3.Connection(":memory:", check_same_thread=False)
        self.Session = self.Database.cursor()
        self.Session.execute('CREATE TABLE urls(url VARCHAR(255));')
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
            if not self.Thread or not str(self.Thread).isdigit():
                self.Thread = 10
            elif not str(self.Thread).isdigit():
                print '[!] Invalid thread format, using 10 by default.'
            if not self.Timeout:
                self.Timeout = 3
            elif not str(self.Timeout).isdigit():
                print '[!] Invalid timeout format, using 3 by default.'
            if not self.GetHomepage():
                return
            self.Thread = int(self.Thread)
            self.Timeout = int(self.Timeout)
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
                    if not self.Queue.qsize() and not len(self.TaskList):
                        print '[*] No URL left, synchronizing tasks.'
                        time.sleep(3)
                        self.Status = False
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
        try:
            head = requests.head('%s://%s/' %(self.Protocol, self.Url), timeout=self.Timeout)
            if 'text' not in head.headers['Content-Type']:
                return
            resp = requests.get('%s://%s/' % (self.Protocol, self.Url), timeout=self.Timeout).text
            UrlList = self.CheckUrlList(resp)
            UrlList = self.ListUpdate(UrlList)
        except requests.Timeout:
            print '[!] Timed out fetching homepage.'
        except requests.ConnectionError:
            print '[!] Failed to connect to server.'
        except Exception ,e:
            print '[!] Failed to fetch url: %s' %(str(e))
        else:
            return 1
        print '[!] Spider got a error, quitting.'
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
        UrlList = self.RemoveFile(UrlList) # Speed should much faster.
        return UrlList


    def ListUpdate(self, UrlList): # Update list.
        session = self.Database.cursor()
        if not UrlList:
            return
        for item in UrlList:
            if not session.execute('SELECT * FROM urls WHERE url="%s";' %(item)).fetchall():
                print '[*] Fetched: %s' %(item)
                session.execute('INSERT INTO urls VALUES ("%s");' %(item))
                self.Queue.put(item)
                self.UrlList.append(item)
        return UrlList
        #     if item not in self.UrlList:
        #         print '[*] Fetched: %s' % (item)
        #         self.Queue.put(item)
        #         self.UrlList.append(item)
        # return UrlList


    def GetPage(self, Url):
        try:
            head = requests.head(Url, timeout=self.Timeout)
            if 'text' not in head.headers['Content-Type']:
                print '[*] Skipping non-text file %s' %(Url)
                return
            if 'zip' in Url:
                print '[W] WARNING: FETCHING A ZIP FILE.'
                print '[W] WARNING: URL: %s' %(Url)
                print '[W] HEADER: %s' %(head.headers['Content-Type'])
                return
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
        while self.Status:
            for item in self.TaskList:
                if not item.isAlive():
                    self.TaskList.remove(item)


    def RemoveFile(self, UrlList): # EXPERIMENT function. For SPECIAL USE only.
        NewUrlList = []
        if not UrlList:
            return
        for item in UrlList:
            if not re.findall('\.ph|\.htm|\.txt|\.js|\.css|\.as|\.action|\.do', item):
                if re.findall('\.zip|\.7z|\.rar|\.jpg|\.png|\.ico|\.doc|\.pp|\.xls|\.sql|\.mdb|\.pdf|\.fl|\.sf', item):
                    return
            NewUrlList.append(item)
        return NewUrlList


def test():
    spider = Spider()
    spider.Url = 'www.phpcms.cn'
    spider.SpiderSite()


test()
