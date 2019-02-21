# Module Handler. This is the dirty part.
import os
import sys
import threading
import queue
import time
import lib.spider.Spider
# Scanners need spider
import lib.scanner.SQLInjectionScanner
import lib.scanner.XSSScanner
# Scanners don't need spider
import lib.scanner.AdminPageFetcher
import lib.scanner.SensitiveFileScanner
# Service scanners.
import lib.scanner.PortCheck
import lib.scanner.FTPPasswordScanner
import lib.scanner.SSHPasswordScanner


class ModuleHandler():
    def __init__(self):
        self.ScannerList = {
            'sql': {'name': 'SQL Injection', 'stat': False, 'item': lib.scanner.SQLInjectionScanner.Scanner()},
            'xss': {'name': 'XSS', 'stat': False, 'item': lib.scanner.XSSScanner.Scanner()},
            'admin': {'name': 'Management Page', 'stat': False, 'item': lib.scanner.AdminPageFetcher.Scanner()},
            'file': {'name': 'Sensitive File', 'stat': False, 'item': lib.scanner.SensitiveFileScanner.Scanner()},
            'ftp': {'name': 'FTP Identify', 'stat': False, 'item': lib.scanner.FTPPasswordScanner.Scanner()},
            'ssh': {'name': 'SSH Identify', 'stat': False, 'item': lib.scanner.SSHPasswordScanner.Scanner()}
        }
        self.Spider = lib.spider.Spider.Spider()
        self.PortScanner = lib.scanner.PortCheck.Scanner()
        self.WebScanFlag = True
        self.ServiceScanFlag = True
        self.Status = False
        self.PortStatus = {21: True, 22: True}
        self.ScanStatus = {'web': 'HOLD', 'service': 'HOLD'}
        self.Thread = 2
        self.Time = 0
        self.UrlList = []
        self.Queue = []
        self.ScanList = []
        self.TaskList = []
        pass


    def Scan(self):
        for item in self.ScannerList.keys():
            if not self.ScannerList[item]['item'].Url:
                print '[!] URL Not specified.'
        if self.WebScanFlag:
            if not self.Spider.Url:
                print '[!] Spider URL Not specified, passing.'
            print '[*] Starting spider.'
            spider = threading.Thread(target=self.Spider.SpiderSite)
            self.TaskList.append(spider)
        if self.ServiceScanFlag:
            if not self.PortScanner.Url:
                print '[!] Port scanner URL Not specified, passing.'
            portscanner = threading.Thread(target=self.PortScanner.Scan)
            self.TaskList.append(portscanner)
        self.Status = True
        for item in self.TaskList:
            item.start()
        taskchecker = threading.Thread(target=self.TaskChecker)
        taskchecker.start()
        Timer = threading.Thread(target=self.Timer)
        Timer.start()
        while self.Status:
            if not len(self.TaskList):
                self.Status = False
        self.UrlList = self.Spider.UrlList
        self.ScannerList['sql']['item'].PageList = self.UrlList
        self.ScannerList['xss']['item'].UrlList = self.UrlList
        for item in self.PortScanner.PortList:
            if item[0] == 21:
                self.PortStatus[21] = True
            if item[0] == 22:
                self.PortStatus[22] = True
        TaskChecker = threading.Thread(target=self.TaskChecker)
        StatReporter = threading.Thread(target=self.StatReporter)
        Timer = threading.Thread(target=self.Timer)
        WebScanner = threading.Thread(target=self.WebScan)
        ServiceScanner = threading.Thread(target=self.WebScan)
        if self.ServiceScanFlag:
            if not self.PortStatus[21]:
                if raw_input('[*] Target port 21 seems closed. Do you want to check it anyway?(y/N)').upper() != 'Y':
                    self.ScannerList['ftp']['stat'] = False
            if not self.PortStatus[22]:
                if raw_input('[*] Target port 22 seems closed. Do you want to check it anyway?(y/N)').upper() != 'Y':
                    self.ScannerList['ssh']['stat'] = False
        if self.WebScanFlag:
            if not self.UrlList:
                if self.ScannerList['sql']['stat']:
                    if raw_input('[*] Failed to get target pages, Do you want to check target SQL Injection anyway?(y/N)').upper() != 'Y':
                        self.ScannerList['sql']['stat'] = False
                if self.ScannerList['xss']['stat']:
                    if raw_input('[*] Failed to get target pages, Do you want to check target XSS vulnerability anyway(y/N)').upper() != 'Y':
                        self.ScannerList['xss']['stat'] = False
        self.Status = True
        if self.WebScanFlag:
            WebScanner.start()
            self.ScanList.append(WebScanner)
        if self.ServiceScanFlag:
            ServiceScanner.start()
            self.ScanList.append(ServiceScanner)
        TaskChecker.start()
        Timer.start()
        StatReporter.start()
        while True:
            for item in self.ScanList:
                if not item.isAlive:
                    self.ScanList.remove(item)
            if not len(self.ScanList):
                break
        self.Status = False
        print '[*] Scan completed.'
        return



    def WebScan(self):
        WebTasks = []
        for item in self.ScannerList.keys():
            if self.ScannerList[item]['name'] in ['ssh', 'ftp']:
                continue
            if self.ScannerList[item]['stat'] == True:
                WebTasks.append([self.ScannerList[item]['name'], self.ScannerList[item]['item']])
        while len(WebTasks):
            if len(self.TaskList) < self.Thread:
                Task = WebTasks.pop()
                print '[*] Now starting %s, %i web scan task(s) left.' %(Task[0], len(WebTasks))
                thread = threading.Thread(target=Task[1].Scan(), name='WebScanner')
                thread.start()
                self.TaskList.append(thread)
            if not len(WebTasks):
                print '[*] All web tasks started, Now synchronizing tasks.'
                for item in self.TaskList:
                    if item.name == 'WebScanner':
                        item.join()
                print '[*] All web tasks completed. Now return.'
        print '[*] Web scan completed'
        return


    def ServiceScan(self):
        ServiceTasks = []
        for item in self.ScannerList.keys():
            if self.ScannerList[item]['name'] not in ['ssh', 'ftp']:
                continue
            if self.ScannerList[item]['stat'] == True:
                ServiceTasks.append([self.ScannerList[item]['name'], self.ScannerList[item]['item']])
        while len(ServiceTasks):
            if len(self.TaskList) < self.Thread:
                Task = ServiceTasks.pop()
                print '[*] Now starting %s, %i service scan task(s) left.' %(Task[0], len(ServiceTasks))
                thread = threading.Thread(target=Task[1].Scan(), name='ServiceScanner')
                thread.start()
                self.TaskList.append(thread)
            if not len(ServiceTasks):
                print '[*] All service tasks started. Now synchronizing tasks.'
                for item in self.TaskList:
                    if item['name'] == 'ServiceScanner':
                        item.join()
                print '[*] All service scanner completed. Now return.'
        print '[*] Service scan completed.'
        return


    def TaskChecker(self):
        time.sleep(1)
        while self.Status:
            for item in self.TaskList:
                if not item.isAlive():
                    self.TaskList.remove(item)
            if not len(self.TaskList):
                print '[*] All tasks completed, stopping task checker.'
                break
        return


    def StatReporter(self):
        while self.Status:
            time.sleep(1)
            print '[*] Web scanner status [%s] Service scanner status [%s]' %(self.ScanStatus['web'], self.ScanStatus['service'])
        return


    def Timer(self):
        self.Time = 0
        while self.Status:
            time.sleep(1)
            self.Time += 1
            print '[*] Cost %i seconds, %i task(s) running.' %(self.Time, len(self.TaskList))
        print '[*] Task completed, costed %i seconds.' %(self.Time)
