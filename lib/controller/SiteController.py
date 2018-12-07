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
        self.cms = {'cms': None, 'version': None, 'website': None}
        self.whois = {
            'stored': False,
            'host': None,
            'register': None,
            'createDate': None,
            'expDate': None,
            'updateDate': None,
            'ownerName': None,
            'ownerCountry': None,
            'ownerAddr': None,
            'ownerTelephone':None,
            'provider': None,
        }
        self.information = {
            'system': None,
            'db': None,
            'waf': None
        }
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
        if self.whois['stored']:
            if raw_input('[*] Previously saved record found. Do you want to refresh it? (Y/N)').upper() != 'Y':
                print '[+] Whois report for %s: ' %(str(self.url))
                print 'Host: %s' %(self.url)
                print 'Registrar: %s' %(self.whois['register'])
                print 'Creation Date: %s' %(self.whois['createDate'])
                print 'Registrar Expiry Date: %s' %(self.whois['expDate'])
                print 'Updated Date: %s' %(str(self.whois['updateDate']))
                print 'Admin Name: %s' %(str(self.whois['ownerName']))
                print 'Admin Address: %s' %(str(self.whois['ownerAddr']))
                print 'Admin Country: %s' %(str(self.whois['ownerCountry']))
                print 'Admin Phone: %s' %(str(self.whois['ownerTelephone']))
                print 'Registrar URL: %s' %(str(self.whois['provider']))
                print '[*] Using saved record, `site update` to clear.'
            else:
                self.whois['stored'] = False
                self.Whois()
        else:
            resp = lib.controller.FunctionLib.Whois(self.url)
            self.whois['host'] = self.url
            self.whois['stored'] = True
            self.whois['register'] = re.findall('Registrar: .*', resp)[0]
            self.whois['createDate'] = re.findall('Creation Date.*', resp)[0]
            self.whois['expDate'] = re.findall('Registrar Expiry Date.*', resp)[0]
            self.whois['updateDate'] = re.findall('Updated Date.*',resp)[0]
            self.whois['ownerName'] = re.findall('Admin Name.*', resp)[0]
            self.whois['ownerAddr'] = re.findall('Admin Street.*', resp)[0]
            self.whois['ownerCountry'] = re.findall('Admin Country.*', resp)[0]
            self.whois['ownerTelephone'] = re.findall('Admin Phone.*', resp)[0]
            self.whois['provider'] = re.findall('Registrar URL.*', resp)[0]
            return
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
        elif mode in ['system', 'db', 'waf']:
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
            elif mode in ['system', 'db', 'waf']:
                if self.information[mode]:
                    if raw_input('[*] Previously saved record found. Do you want to refresh it? (Y/N)').upper() != 'Y':
                        self.GetStoragedInfo(mode)
                        return
                    else:
                        self.information[mode] = None
                if mode == 'system':
                    self.information['system'] = self.FingerprintIdentifier.CheckSystem()
                elif mode == 'waf':
                    self.information['db'] = self.FingerprintIdentifier.CheckDatabase()
                else:
                    self.information['waf'] = self.FingerprintIdentifier.CheckWaf()
            else:
                print '[!] Invalid mode.'
        except Exception, e:
            print '[!] Failed to check site information: %s' %(str(e))
        return
