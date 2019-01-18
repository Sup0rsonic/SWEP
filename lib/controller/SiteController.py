import domeko
import requests
import re
import socket
import sys
import lib.controller.FunctionLib
import lib.fingerprint.FingerprintIdentifier

# SWEP site class

class site():
    def __init__(self): # Site information
        self.url = None
        self.port = None
        self.addr = None
        self.cms = {'cms': None, 'version': None}
        self.information = {'system': None, 'db': None, 'waf': None, 'language': None}
        self.whois = None
        self.sites = None
        self.subnet = None
        self.FingerprintIdentifier = lib.fingerprint.FingerprintIdentifier.FingerprintIdentifier()
        self.Name = None
        self.domain = None


    def GetAddr(self):
        try:
            if self.addr:
                print '[+] The address of target from db is: %s.' %(str(self.addr))
            addr = socket.gethostbyname(self.url)
            print '[+] The address of target is: %s' %(str(addr))
            self.addr = addr
        except Exception, e:
            print '[!] Error get target address: %s' %(str(e))
        print '[*] Get address complete'
        return

    def cmsIdentify(self):
        if self.cms:
            if raw_input('[*] Previously saved record found. Do you want to refresh it? (Y/N)').upper() != 'Y':
                print '[+] Total %s potential CMS.' %(str(len(self.cms)))
                for item in self.cms:
                    print '[+] Potential CMS of %s is: %s' %(self.url, str(item))
                    return
            else:
                self.cms = []
        else:
            self.cms = self.FingerprintIdentifier.CheckSiteCMS()
        return

    def Whois(self):
        if not self.whois:
            resp = lib.controller.FunctionLib.Whois(self.url)
            self.whois = resp
        else:
            if raw_input('[*] Previously saved recored found. Do you want to refresh it (Y/N)').upper() != 'Y':
                print self.whois
            else:
                self.whois = lib.controller.FunctionLib.Whois(self.url)
        return

    def GetSubnet(self):
        try:
            print '[*] Getting subnet.'
            self.subnet = lib.controller.FunctionLib.Subnet(self.url,'c')
        except Exception, e:
            print '[!] Error getting subnet: %s' %(str(e))
        return self.subnet

    def GetSite(self):
        try:
            if self.sites:
                if raw_input('[*] Previously saved record found. Do you want to refresh it? (Y/N)').upper() != 'Y':
                    print '[+] Using stored site information.'
                    print '[+] %i sites found on %s.' %(len(self.sites), self.url)
                    for item in self.sites:
                        print '  |  [+] Site title: %s' %(item['title'])
                        print '  |  [+] Site URL: %s' %(item['domain'])
                    return
                else:
                    self.sites = None
            print '[*] Trying to get same ip site information.'
            self.sites = lib.controller.FunctionLib.GetSameIP(self.url)
        except Exception,e :
            print '[!] Error getting same-ip site information: %s' %(str(e))
        return self.sites

    def GetStoragedInfo(self,mode): # Need to rewrite: Format
        if mode in ['cms', 'version']:
            if self.cms[mode]:
                print '[+] Using stored information.'
                print '[+] The %s of %s is %s.' %(mode, self.url, self.cms[mode])
        elif mode in ['system', 'db', 'waf', 'language']:
            if self.information[mode]:
                print '[+] Using stored information.'
                print '[+] The %s of %s is %s.' %(mode, self.url, self.information[mode])
        else:
            print '[*] Mode not specified.'
            return


    def CheckInformation(self, mode):
        if not self.FingerprintIdentifier.url or not self.FingerprintIdentifier.site:
            self.FingerprintIdentifier.url = self.url
            self.FingerprintIdentifier.site = self.url
        try:
            if mode in ['cms', 'version']:
                if self.cms[mode]:
                    if raw_input('[*] Previously saved record found. Do you want to refresh it? (Y/N)') != 'Y':
                        self.GetStoragedInfo(mode)
                        return
                    else:
                        self.cms[mode] = None
                if mode == 'cms':
                    self.cms['cms'] = self.FingerprintIdentifier.CheckSiteCMS()
                else:
                    self.cms['version'] = self.FingerprintIdentifier.CheckCMSVersion()
            elif mode in ['system', 'db', 'waf', 'language']:
                if self.information[mode]:
                    if raw_input('[*] Previously saved record found. Do you want to refresh it? (Y/N)').upper() != 'Y':
                        self.GetStoragedInfo(mode)
                        return
                    else:
                        self.information[mode] = None
                if mode == 'system':
                    self.information['system'] = self.FingerprintIdentifier.CheckSystem()
                elif mode == 'db':
                    self.information['db'] = self.FingerprintIdentifier.CheckDatabase()
                elif mode == 'waf':
                    self.information['waf'] = self.FingerprintIdentifier.CheckWaf()
                elif mode == 'language':
                    self.information['language'] = self.FingerprintIdentifier.CheckSiteLanguage()
                else:
                    print '[*] Invalid mode.'
            else:
                print '[!] Invalid mode.'
        except Exception, e:
            print '[!] Failed to check site information: %s' %(str(e))
        return
