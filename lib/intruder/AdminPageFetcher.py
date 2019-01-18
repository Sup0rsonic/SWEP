import requests
import os
import queue
import threading
import time


class AdminPageIdentifer():
    def __init__(self):
        self.Url = None
        self.Thread = 10
        self.Timeout = 3
        self.Protocol = 'http'
        self.path = os.path.dirname(os.path.abspath(__file__))
        self.AdminPageDict = None
        self.SiteAdminPage = []
        self.AdminPageList = self.path + '/../../WordLists/adminpages'
        self.Queue = queue.Queue()
        self._Counter = 0
        self._Time = 0
        pass


    def FetchAdminPage(self):
        if not self.Url:
            print '[!] URL not specified.'
            return
        elif not self.AdminPageDict:
            print '[*] Admin page list not specified, using default.'
            try:
                self.AdminPageDict = open(self.AdminPageList, 'r').read().split('\n')
            except Exception, e:
                print '[!] Admin page list file not exist, Quitting.'
                return
        try:
            print '[*] Starting admin page fetcher.'
            timer = threading.Thread(target=self._Timer)
            timer.setDaemon(True)
            timer.start()
            counter = threading.Thread(target=self.Counter)
            counter.setDaemon(True)
            counter.start()
            for item in self.AdminPageDict:
                self.Queue.put(item)
            while self.Queue.qsize() != 0:
                if self.Thread > self._Counter:
                    threading.Thread(target=self._AdminPageFetcher, args=[self.Queue.get()]).start()
                    self._Counter += 1
        except KeyboardInterrupt:
            print '[*] User quit ,stopping.'
        except Exception, e:
            print '[!] Failed to fetch page: %s' %(str(e))
        print '[*] Admin page fetch completed, %s page(s) found, cost %s second(s)' %(int(len(self.SiteAdminPage)), int(self._Time))
        return self.SiteAdminPage


    def _Timer(self):
        while True:
            time.sleep(1)
            self._Time += 1


    def Counter(self):
        while True:
            time.sleep(10)
            print '[*] Time cost: %i second(s), %i thread(s) running, %i page(s) fetched.' %(self._Time, self._Counter, len(self.SiteAdminPage))


    def _AdminPageFetcher(self, page):
        url = '%s://%s/%s' %(self.Protocol, self.Url, page)
        try:
            resp = requests.get(url, timeout=int(self.Timeout))
            if resp.status_code != 404 and 'not found' not in resp.text and '404' not in resp.text:
                self.SiteAdminPage.append(url)
                print '[+] Fetched admin page: %s' %(url)
        except requests.Timeout:
            print '[*] Request timeout fetching page %s' %(str(url))
        except Exception, e:
            print '[!] Failed fetching an admin page: %s' %(str(e))
        self._Counter -= 1
        return


def test():
    scanner = AdminPageIdentifer()
    scanner.Url = "www.dedecms.com"
    scanner.FetchAdminPage()

