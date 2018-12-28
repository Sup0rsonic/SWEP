import socket
import json
import domeko
import requests
import re
import sys
import os
import lib.config
import lib.db
import threading
import lib.fingerprint.FingerprintIdentifier
import pickle

# Information gather functions library

def Whois(site):
    sess = socket.socket(2,1)
    try:
        sess.connect(('192.30.45.30',43))
        sess.send(str(site) + '\n')
        print '[+] Whois report for %s' %(str(site))
        resp = str(sess.recv(10240))
        print resp
    except Exception, e:
        print '[!] Whois query failed, %s' %(str(e))
        resp = None
    print '[*] Whois query completed.'
    return resp

def Subnet(site,mode):
    addr = GetAddr(site)
    list = []
    try:
        if mode == 'c':
            addr = re.findall('.*\.*\.*\.',addr)[0]
            for i in range(0,254):
                list.append(addr + str(i))
        elif mode == 'b':
            if raw_input('[*] You are trying to scan a B-Class subnet. Continue? (Y/N)').upper() != 'Y':
                return
            addr = re.findall('.*\.*\.',addr)[0]
            for i in range(0,254):
                for j in range(0,254):
                    list.append(addr + str(i) + '.' + str(j))
        else:
            print '[!] No subnet mode provided.'
            return
        for i in list:
            json = domeko.scan(str(i))
        print '[*] Scan completed.'
    except Exception, e:
        print '[!] Failed to check subnet: %s' %(str(e))
        return
    return json

def GetAddr(site):
    try:
        addr = socket.gethostbyname(str(site))
        print '[+] Address of %s is %s.' %(str(site), str(addr))
        return addr
    except Exception, e:
        print '[!] Failed to get address of %s: %s' %(str(site), str(e))


def GetPage(site):
    try:
        resp = requests.get('http://%s/' %(site))
        print '[*] Response Code %s' %(resp.status_code)
        print '[*] Response Header %s' %(resp.headers)
        print '[*] Response Body\n %s' %(resp.text)
    except Exception, e:
        resp = None
        print '[!] Error1: %s' %str(e)
    return resp


def Fingerprint(site, mode):
    FingerprintIdentifier = lib.fingerprint.FingerprintIdentifier.FingerprintIdentifier()
    FingerprintIdentifier.site = site
    FingerprintIdentifier.CheckMode('tmp')
    FingerprintIdentifier.CheckSiteLanguage() # Unnecessary?
    if mode == 'cms':
        cms = FingerprintIdentifier.CheckSiteCMS()
    elif mode == 'db':
        db = FingerprintIdentifier.CheckDatabase()
    elif mode == 'version':
        FingerprintIdentifier.CheckSiteCMS()
        FingerprintIdentifier.CheckCMSVersion()
    elif mode == 'waf':
        waf = FingerprintIdentifier.CheckWaf()
    elif mode == 'language':
        language = FingerprintIdentifier.CheckSiteLanguage()
    pass


def GetSameIP(site):
    try:
        addr = socket.gethostbyname(str(site))
        SiteList = domeko.scan(addr)
    except Exception, e:
        print '[!] Failed check domain: %s' %(str(e))
        return None
    return SiteList


def RemoveDuplicate(listRaw):
    listNew = []
    for i in listRaw:
        if i not in listNew:
            listNew.append(i)
    return listNew


def ClassSerialize(Object):
    try:
        Class = pickle.dumps(Object, protocol=2)
    except Exception ,e:
        print '[!] Failed to serialize object: %s' %(str(e))
        return None
    return Class


def ClassUnseralize(Object):
    try:
        Class = pickle.loads(Object)
    except Exception, e:
        print '[!] Failed to unserialize object: %s' %(str(e))
        return None
    return Class


