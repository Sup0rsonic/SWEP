import requests
import BeautifulSoup
import Queue
import re
import threading


class Spider():
    def __init__(self):
        self.url = None
        self._WebRootPage = None
        self.UrlList = []
        self._ParmList = {}
        self._DuplicateUrlList = []
        self.Threads = 10
        self._Counter = 0
        self.Protocol = 'http'
        self.queue = Queue.Queue()


    def SpiderSite(self):
        if self.url:
            if not self.Protocol:
                print '[!] Protocol not specified, using HTTP by default.'
                self.Protocol = 'http'
            self._WebRootPage = '%s://%s/' %(self.Protocol, self.url)
        else:
            print '[!] Error getting site: URL not specified.'
        UrlList = self.GetHomepage()
        Robots = self.GetRobots()
        for url in Robots:
            UrlList.append(url)
        print '[+] Fetched %s urls from robots.' %(str(len(Robots)))
        UrlList = self.CheckUrlList(UrlList)
        self.UrlList = self.LoadPage(UrlList)
        while not self.queue.empty():
            if self._Counter < self.Threads:
                thread = threading.Thread(target=self.GetPage, args=[self.queue.get()])
                thread.start()
                self._Counter += 1
        return self.UrlList


    def GetHomepage(self):
        try:
            resp = requests.get(self._WebRootPage).text
            UrlList = self.GetPageUrl(resp)
            UrlList = self.CheckUrlList(UrlList)
        except Exception, e:
            print '[!] Error getting homepage: %s' %(str(e))
            UrlList = ''
        return UrlList


    def GetPageUrl(self, page): # Fetch URL from page, Return List.
        UrlList = []
        try:
            soup = BeautifulSoup.BeautifulSoup(page)
            for item in soup.findAll('a'):
                UrlList.append(item.get('href').lstrip('/'))
            print '[*] Fetched %s urls.' %(str(len(UrlList)))
        except Exception, e:
            print '[!] Error fetching url: %s.' %(str(e))
        return UrlList



    def CheckUrl(self, url): # Get string URL, Check avilable URL, Return a url.
        try:
            if re.findall(r'^(?![/]{2}|http[s]?://).*', url):
                pass
            else:
                if re.findall(self.url, url):
                    url = re.sub('^([/]{2}|http[s]?://)%s' % (self.url.replace('.', '\.')), '', url)
                    url = url.lstrip('/')
                else:
                    url = None
            if url:
                if re.findall('\.jpg|\.gif|\.jpeg|\.js|\.pdf|\.doc|\.png|\.bmp|\.css|\.xml|\.xls|\.json|\.ppt|\.psd', url):
                    url = None
        except Exception, e:
            print '[!] Error checking url: %s, resuming next' %(str(e))
            url = None
        return url



    def GetPage(self, url): # Fetch page.
        try:
            resp = requests.get(self._WebRootPage+url).text
            UrlList = self.GetPageUrl(resp)
            UrlList = self.CheckUrlList(UrlList)
            self.LoadPage(UrlList)
        except Exception, e:
            print '[!] Error getting page: %s' %(str(e))
            UrlList = []
        self._Counter -= 1
        return UrlList


    def CheckUrlList(self, UrlList): # Get a literable list, Check availability, Return a list.
        NewUrlList = []
        for url in UrlList:
            url = self.CheckUrl(url)
            if url and url != u'#' and url != u'':
                NewUrlList.append(url)
        return NewUrlList


    def LoadPage(self, page): # Load pages without other actions but check duplicate and store into queue and urllist
        NewUrlList = []
        UrlList = self.CheckDuplicate(page)
        for page in UrlList:
            self.queue.put(page)
            NewUrlList.append(page)
        return NewUrlList


    def CheckDuplicate(self, list): # Check urls, feed them into duplicate list.
        UrlList = []
        PageList = []
        for url in list:
            PageUrl = url.split('?')[0]
            if PageUrl not in PageList:
                PageList.append(PageUrl)
                pass
            else:
                continue
            if url not in self._DuplicateUrlList:
                UrlList.append(url)
                self._DuplicateUrlList.append(url)
        return UrlList


    def GetRobots(self):
        UrlList = []
        try:
            resp = requests.get(self._WebRootPage).text
            UrlList = re.findall('[Aa]?llow: /(.*)$', resp)
        except Exception, e:
            print '[!] Failed to fetch robots: %s' %(str(e))
        return UrlList

    def CheckParms(self): # Check pages, fetch parms, stat parms, return in a dict. dict will be like # List format: {url:{parm:val}}
        ParmDict = {}
        try:
            for url in self.UrlList:
                url, parm = re.split('\?', url)
                if url == u'' or '' or None:
                    url = '/'
                if '&' in parm:
                    parmList = parm.split('&')
                else:
                    continue
                for parm in parmList:
                    param, value = parm.split('=')
                    if url not in ParmDict:
                        ParmDict[url] = {}
                    if not ParmDict[url].has_key(param):
                        ParmDict[url][param] = value
                print ParmDict
                return
        except Exception, e:
            print '[!] Error checking parameter: %s.' %(e)


def test():
    spider = Spider()
    spider.url = 'www.katun.me'
    UrlList = spider.SpiderSite()
    print '*' + '-' * 30 + '*'
    for url in UrlList:
        print '[+] Fetched: %s' %(str(url))
