import requests
import lib.fingerprint.FingerprintLoader
import lib.controller.FunctionLib
import re
import threading
import hashlib
import queue
import socket
import sys
import urllib2
import time

class FingerprintIdentifier():
    def __init__(self):
        self.site = None
        self.url = None
        self._FingerprintLoader = lib.fingerprint.FingerprintLoader.FingerprintLoader()
        self._counter = 0
        self.RawResp = None
        self.CMS = []
        self.WAF = []
        self.OperatingSystem = []
        self.Database = []
        self.SiteLanguage = None
        self._thread = 10
        self._CMSVerison = []
        self._ThreadLock = False


    def CheckMode(self,mode):
        if mode == 'tmp':
            self.url = self.site
        return


    def CheckSiteFingerprint(self):
        try:
            self.RawResp = requests.get('http://%s/' %(self.url))
            self.SiteLanguage = self.CheckSiteLanguage()
            self.CMS = self.CheckSiteCMS()
        except Exception, e:
            print '[!] Failed to check fingerprint: %s' %(str(e))
            print sys.exc_info()[0]
        pass


    def CheckSiteLanguage(self):
        self.RawResp = requests.get('http://%s/' % (self.url))
        HeadersText = ''
        for item in self.RawResp.headers.keys():
            HeadersText += str(item)
            HeadersText += ':'
            HeadersText += self.RawResp.headers[item]
            HeadersText += '\n'
        if re.findall('asp|aspx|iis|microsoft|windows server',HeadersText, re.I+re.M):
            self.SiteLanguage = 'dotnet'
        elif re.findall('php',HeadersText, re.I+re.M):
            self.SiteLanguage = 'php'
        elif re.findall('jsp|coyote|tomcat|java',HeadersText, re.I+re.M):
            self.SiteLanguage = 'jsp'
        else:
            self.SiteLanguage = 'other'
        if self.SiteLanguage:
            print '[+] Language of %s is %s' %(str(self.url), self.SiteLanguage)
        else:
            print '[*] No language found.'
        print '[+] Language check complete.'
        return self.SiteLanguage


    def LoadFingerprint(self):
        try:
            self._FingerprintLoader.Language = self.SiteLanguage
            FingerprintList = self._FingerprintLoader.LoadSiteFingerprint()
        except Exception,e:
            print '[!] Error loading fingerprint: %s' %(str(e))
            FingerprintList = None
        return FingerprintList


    def CheckSiteCMS(self):

        self.SiteLanguage = self.CheckSiteLanguage()
        CMSFingerprints = self.LoadFingerprint()
        CMSList = []
        if not CMSFingerprints:
            return None
        HashList = CMSFingerprints['hashes']
        PageList = CMSFingerprints['pages']
        HeaderList = CMSFingerprints['headers']
        try:
            self.CheckHash(HashList)
            self.CheckPage(PageList)
            self.CheckHeader(HeaderList)
            if self.CMS:
                if len(self.CMS):
                    print '[+] %s potential CMS found: ' % (str(len(self.CMS)))
                    for item in self.CMS:
                        print '[+] Potential CMS: %s' %(str(item))
                else:
                    print '[*] How do you see this?' # If you see this, Hello.
            else:
                print '[*] CMS not found.'
        except Exception, e:
            print '[!] Failed to check CMS: %s' %(str(e))
        print '[+] CMS check completed.'
        return


    def CheckHash(self, json):
        TaskList = queue.Queue()
        for item in json:
            TaskList.put(item)
        while TaskList.qsize() != 0:
            if self._thread > self._counter:
                thread = threading.Thread(target=self._HashChecker, args=[TaskList.get()])
                thread.start()
                if TaskList.empty():
                    thread.join()


    def _HashChecker(self, json):
        try:
            url, cms, hash = json.split('|')
        except Exception, e:
            print '[!] Failed to unpack json: %s' %(str(e))
            return
        try:
            resp = urllib2.urlopen('http://%s/%s' %(self.url, url), timeout=3).read()
            if hashlib.md5(resp).hexdigest() == hash:
                if cms not in self.CMS:
                    print '[+] Potential CMS: %s' % (str(cms))
                    self.CMS.append(cms)
        except urllib2.HTTPError:
            pass
        except Exception, e:
            print '[!] Failed checking cms: %s' %(str(e))
        return




    def CheckPage(self,json):
        TaskList = queue.Queue()
        for i in json:
            TaskList.put(i)
        while not TaskList.empty():
            if self._counter < self._thread:
                self._counter += 1
                thread = threading.Thread(target=self._PageChecker, args=[TaskList.get()])
                thread.start()
        while self._ThreadLock:
            pass
    pass


    def _PageChecker(self,task):
        try:
            url, cms, code = re.split('\|', task)
            self._ThreadLock = True
            if requests.get('http://%s%s' %(self.url, url)).status_code == int(code):
                self.CMS.append(cms)
                print '[+] Potential CMS of site %s: %s' %(self.url, cms)
        except Exception,e :
            print str(e)
        self._counter -= 1
        self._ThreadLock = False
        return


    def CheckHeader(self,json):
        TaskList = queue.Queue()
        for i in json:
            TaskList.put(i)
        while not TaskList.empty():
            if self._counter < self._thread:
                self._counter += 1
                thread = threading.Thread(target=self._HeaderChecker, args=(TaskList.get()))
                thread.setDaemon(True)
                thread.start()
        return


    def _HeaderChecker(self,task):
        try:
            url, cms, header = re.split('\|', task)
            if re.findall(header, requests.get('http://%s%s' %(self.url, url)).headers):
                self.CMS.append(cms)
                print '[+] Potential CMS of site %s: %s' %(self.url, cms)
        except Exception, e:
            print str(e)
        self._counter -= 1
        pass


    def FetchPage(self):
        try:
            return requests.get(self.url).text
        except Exception, e:
            return None


    def _LoadCMSVersion(self):
        CMSVersionList = []
        if not self.CMS:
            print '[!] CMS not identified.'
            return
        for i in self.CMS:
            CMSVersionList.append(self._FingerprintLoader.LoadCmsVerionFingerprint())
        return CMSVersionList


    def CheckCMSVersion(self):
        CMSVersionList = self._LoadCMSVersion()
        if not CMSVersionList:
            print '[!] CMS Version of %s is not available.' %(str(self.CMS))
            return
        if not len(CMSVersionList):
            print '[!] Version check for this cms is not available.'
        for cms in CMSVersionList:
            CMSVersioNFingerprintList = cms['version']
            thread = threading.Thread(target=self._CMSVersionChecker, args=(CMSVersioNFingerprintList))
            thread.setDaemon(True)
            thread.start()
        return

    def _CMSVersionChecker(self,json):
        try:
            CMSVersionList = queue.Queue()
            for i in json:
                CMSVersionList.put(i)
            while CMSVersionList.qsize() != 0:
                if self._counter < self._thread:
                    self._counter += 1
                    thread = threading.Thread(target=self._CheckKeyword,args=(CMSVersionList.get()))
                    thread.start()
        except Exception, e:
            print '[!] Error loading CMS version: %s' %(str(e))
        return


    def _CheckKeyword(self,task):
        version, url, keyword = re.split('\|', task)
        try:
            if re.findall(keyword, requests.get('http://%s%s' %(self.url, url)).text):
                self._CMSVerison.append(version)
        except Exception, e:
            print '[!] Error checking CMS version: %s' %(str(e))
        return


    def CheckWaf(self):
        WafList = self._FingerprintLoader.LoadWafFingerprint()
        if not WafList:
            print '[!] Unable to load WAF fingerprint.'
        try:
            resp = requests.get('http://%s/?union select 1 and 1=2 and updatexml(1,concat(0x7e,(0x23333),0x7e),1) <script>alert(1)</script> {{1+1}}' %(self.url)).text
            if not resp:
                print '[!] Error loading WAF fingerprint.'
                return
            WafFingerprint = WafList['waf']
            for fingerprint in WafFingerprint:
                waf, fingerprint = re.split('\|', fingerprint)
                if re.findall(fingerprint, resp):
                    self.WAF.append(waf)
            if len(self.WAF) == 0:
                print '[+] Check completed, No waf identified.'
            else:
                print '[+] Check completed, waf identified:'
                for waf in self.WAF:
                    print '[+] WAF of %s is %s' %(self.url, waf)
        except requests.ConnectionError:
            print '[*] RST flag stopped. WAF identify is not available.'
            return
        except Exception, e:
            print '[!] Error connecting site: %s' %(str(e))
            return
        return self.WAF


    def _WafChecker(self,task):
        pass


    def CheckDatabase(self):
        sess = socket.socket(2,1)
        sess.settimeout(3)
        try:
            print '[*] Starting connection scan.'
            sess.connect((self.site,1433))
            self.Database = 'mssql (open)'
        except:
            pass
            try:
                sess = socket.socket(2,1)
                sess.settimeout(3)
                sess.connect((self.site,3306))
                buf = sess.recv(1024)
                if buf.find('mariadb'):
                    self.Database = 'mariadb (open)'
                else:
                    self.Database = 'mysql (open)'
            except socket.timeout:
                pass
            except Exception, e:
                print '[!] Error during connection scan: %s' %(str(e))
            pass
        print '[*] Connection scan completed.'
        if self.Database:
            print '[+] Database type: %s' %(self.Database)
            return self.Database
        try:
            Headers = requests.get('http://%s/' %(self.site)).headers
            RawHeader = ''
            for item in Headers:
                RawHeader += item
                RawHeader += ':'
                RawHeader += Headers[item]
                RawHeader += '\n'
            Headers = RawHeader
            if re.findall('(?i)mysql', Headers):
                self.Database = 'mysql'
            elif re.findall('(?i)mariadb', Headers):
                self.Database = 'mariadb'
            elif re.findall('(?i)SQLInjectionScanner server', Headers):
                self.Database = 'mssql'
            elif re.findall('(?i)mongodb', Headers):
                self.Database = 'mongodb'
            elif re.findall('postgre', Headers):
                self.Database = 'postgre SQLInjectionScanner'
            else:
                self.Database = 'unknown'
            print '[+] Database type: %s' %(self.Database)
        except Exception, e:
            print '[!] Error during header scan: %s' %(str(e))
        print '[+] Database check completed.'
        return self.Database


    def CheckSystem(self):
        sess = socket.socket(2,1)
        sess.settimeout(3)
        try:
            Headers = requests.get('http://%s/' %(self.site)).headers
            if re.findall('(?i)iis|asp|aspx|windows|\.net|microsoft',str(Headers)):
                self.OperatingSystem = 'Windows'
            elif re.findall('(?i)Linux|ubuntu|centos|redhat|debian|manjaro|arch|deepin|mint|suse|oracle', str(Headers)):
                self.OperatingSystem = 'Linux'
            elif re.findall('(?i)bsd', str(Headers)):
                self.OperatingSystem = 'BSD'
            elif re.findall('(?i)unix', str(Headers)):
                self.OperatingSystem = 'Unix'
            else:
                self.OperatingSystem = None
        except Exception, e:
            print '[!] Error getting server system: %s' %(str(e))
        if self.OperatingSystem:
            print '[+] Server system is %s' %(str(self.OperatingSystem))
            return self.OperatingSystem
        try:
            PortList = {21: '*nix', 3389: 'windows', 445: 'windows', 1433: 'windows'}
            for port in PortList.keys():
                try:
                    sess.connect((self.url, port))
                    self.OperatingSystem = PortList[port]
                except socket.timeout or socket.error:
                    pass
        except Exception, e:
            print '[!] Error checking system: %s' %(str(e))
            pass
        if not self.OperatingSystem:
            self.OperatingSystem = 'Unknown'
        print '[+] Server system is %s' %(self.OperatingSystem)
        return self.OperatingSystem


