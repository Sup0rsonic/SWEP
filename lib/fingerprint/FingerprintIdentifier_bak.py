import requests
import re
import lib.controller.FunctionLib
import FingerprintManager
import fingerprints.FingerprintLoader
import threading
import hashlib


class FingerprintIdentifier():
    def __init__(self):
        self.FingerprintLoader = fingerprints.FingerprintLoader.FingerprintLoader()
        self.site = None
        self.cms = None
        self.version = None
        self.CmsList = None
        self.CmsLanguage = None
        self.CmsLoader = fingerprints.FingerprintLoader.FingerprintLoader()
        self.SiteCMS = []



    def LoadInformation(self,site): # Load inital information
        try:
            resp = requests.get('http://%s/' %(site))
            self.StatusCode = resp.status_code
            self.ResponseHeader = resp.headers
            self.SiteCookie = resp.cookies
            self.PageIndex = resp.text
            self.Url = resp.url

        except Exception, e:
            print '[!] Error getting homepage %s' %(str(e))
            return False
        return True


    def CheckCMSInformation(self,site): # Load CMS list
        if not self.LoadInformation(site):
            print '[!] Error fetching site information'
            return
        try:
            self.CmsList = self.FingerprintLoader.CmsList
        except:
            print '[!] Failed to load CMS list.'
            return
        return self.CmsList

    def CheckLanguage(self,site):
        langlist = []
        if not self.PageIndex:
            homepage = requests.get('http://%s/' %(site)).text
        else:
            homepage = self.PageIndex
        if re.findall('<a href=/.*\.php.*>', homepage):
            langlist.append('php')
        if re.findall('<a href=/.*\.asp>.*', homepage):
            langlist.append('asp')
        if re.findall('<a href=/.*\.jsp>.*', homepage):
            langlist.append('jsp')
        if re.findall('<a href=/.*\.(?!asp|php|jsp).*>', homepage):
            langlist.append('other')
        for i in langlist:
            print '[*] Potential CMS language: %s' %(str(i))
        self.CmsLanguage = langlist
        return langlist


    def CheckCMSType(self,site,json):
        CmsType = []
        url = 'http://%s' %(site)
        resp = requests.get(url)
        for name in json:
            try: # Extract data
                header = json[name]['header']
                hash = json[name]['hash']
                file = json[name]['file']
            except:
                print '[!] Error extracting hash.'
                return
            for i in header:
                if re.match(i,resp.text):
                    CmsType.append(name)
            for page in hash:
                try:
                    page = requests.get('http://%s/%s' %(site,page)).text
                    if hashlib.md5(page).hexdigest() == hash[url]:
                        CmsType.append(name)
                except Exception, e:
                    print '[!] Error fetching page %s: %s' %(str(url),e)
                    pass
            for page in file:
                try:
                    if requests.get(url + page).status_code == file['page']:
                        CmsType.append(name)
                except Exception, e:
                    print '[!] Error fetching page %s: %s' %(str(page), e)
        return self.RemoveDuplicate(CmsType)


    def _VersionChecker(self,task):
        pass


    def LoadCMSVersion(self):
        CmsVersionList = []
        if len(self.SiteCMS) == 0:
            print '[!] Site cms not find.'
            return
        for i in self.SiteCMS:
            try:
                CmsVersion = self.FingerprintLoader.LoadCmsVersionFingerprint(i)
                CmsVersionList.append(CmsVersion)
            except:
                return
        return CmsVersionList


    def RemoveDuplicate(self,listRaw):
        listNew = []
        for i in listRaw:
            if i not in listNew:
                listNew.append(i)
        return listNew


    def CheckCms(self,site):
        if self.LoadInformation(site) == False:
            print '[*] Failed to load information.'
            return
        language = self.CheckLanguage(site)
        for lang in language:
            thread = threading.Thread(target=self.CheckCmsByLanguage,args=(site,lang))
            thread.setDaemon(True)
            thread.start()
        print '[+] CMS Check completed.'
        print '[+] Potential CMS:'
        for i in self.SiteCMS:
            print str(i)
        if raw_input('Do you want to check CMS version? (Y/N) ').upper() == 'Y':
            pass
        else:
            pass
        print '[*] CMS check completed.'
        return


    def CheckCmsByLanguage(self,language,site):
        CmsList = self.CmsLoader.LoadCmsNameFingerprint(language)
        SiteCMS = self.CheckCMSType(site,CmsList)
        for i in SiteCMS:
            self.SiteCMS.append(i)
        return 0