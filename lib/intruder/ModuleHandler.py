import os
import lib.config
import lib.spider.Spider
import lib.scanner.AdminPageFetcher
import lib.scanner.FTPPasswordScanner
import lib.scanner.SQLInjectionScanner_dev
import lib.scanner.HashCracker
import lib.scanner.SSHPasswordScanner
import lib.scanner.SensitiveFileScanner
import lib.scanner.XSSScanner
import lib.scanner.PortCheck
import lib.controller.sqlmapController
import lib.controller.ExploitController
import lib.controller.FunctionLib
import lib.fingerprint.FingerprintIdentifier
import PrintHandler


class ModuleHandler():
    def __init__(self):
        self.OptionDict = {'Spider': False, 'Admin': False, 'FTP': False, 'SQLi': False, 'Hash': False, 'SSH': False, 'File': False, 'XSS': False, 'CMSidf': False, 'CMSExp': False, 'Port': False}
        self.Url = None
        self.Threads = None
        self.UsernameFile = None
        self.PasswordFile = None
        self.UserPassFile = None
        self.SSHPort = None
        self.FTPPort = None
        self.Address = None
        self.SensitiveFileList = None
        self.ManagementFileList = None
        self.ArgumentList = []
        self.ScannerList = []
        self.InformationDict = {}
        self.Dir = os.path.dirname(os.path.abspath(__file__))
        self.PrintHandler = PrintHandler.PrintController()
        pass


    def LoadArguments(self):
        pass


    def LoadModules(self):
        try:
            if self.OptionDict['Spider']:
                self.Spider = lib.spider.Spider.Spider()
                self.ScannerList.append(self.Spider)
            if self.OptionDict['Admin']:
                self.AdminFetcher = lib.scanner.AdminPageFetcher.Scanner()
                self.ScannerList.append(self.AdminFetcher)
            if self.OptionDict['FTP']:
                self.FTPBruteforcer = lib.scanner.FTPPasswordScanner.Scanner()
                self.ScannerList.append(self.FTPBruteforcer)
            if self.OptionDict['SQLi']:
                self.SQLInjectionChecker = lib.scanner.SQLInjectionScanner_dev.Scanner()
                self.ScannerList.append(self.SQLInjectionChecker)
            if self.OptionDict['Hash']:
                self.HashChecker = lib.scanner.HashCracker.Scanner()
                self.ScannerList.append(self.SQLInjectionChecker)
            if self.OptionDict['SSH']:
                self.SSHPasswordScanner = lib.scanner.SSHPasswordScanner.Scanner()
                self.ScannerList.append(self.SSHPasswordScanner)
            if self.OptionDict['File']:
                self.SensitiveFileScanner = lib.scanner.SensitiveFileScanner.Scanner()
                self.ScannerList.append(self.SensitiveFileScanner)
            if self.OptionDict['XSS']:
                self.XSSScanner = lib.scanner.XSSScanner.Scanner()
                self.ScannerList.append(self.XSSScanner)
            if self.OptionDict['CMSidf']:
                self.CMSIdentifier = lib.fingerprint.FingerprintIdentifier.FingerprintIdentifier()
                self.ScannerList.append(self.CMSIdentifier)
            if self.OptionDict['CMSExp']:
                self.CMSExploitloader = lib.controller.ExploitController.ExploitController()
                self.ScannerList.append(self.CMSExploitloader)
            if self.OptionDict['Port']:
                self.PortChecker = lib.scanner.PortCheck.Scanner()
                self.ScannerList.append(self.PortChecker)
        except Exception, e:
            print '[!] Failed to load modules: %s' %(str(e))
        print '[*] Module load completed.'
        return


    def StartCheck(self):
        if not self.Url:
            print '[!] URL Not specified.'
            return
        if not self.Threads:
            print '[!] Threads not specified, Using 10 by default.'
            self.Threads = 10
        if not os.path.isfile(self.UserPassFile):
            print '[*] Userpass file not found.'
            if not os.path.isfile(self.UsernameFile):
                print '[!] Username file not found, using module default(if there is).'
                self.UsernameFile = None
            if not os.path.isfile(self.PasswordFile):
                print '[!] Password file not found, using module default(if there is).'
                self.UsernameFile = None
        else:
            pass
        if not self.SSHPort:
            print '[!] SSH port not specified, using 22 by default.'
            self.SSHPort = 22
        if not self.FTPPort:
            print '[!] FTP port not specified, using 21 by default.'
            self.FTPPort = 21
        if not os.path.isfile(self.SensitiveFileList):
            print '[!] Sensitive file list not found, using module default(if there is).'
        if not os.path.isfile(self.ManagementFileList):
            print '[!] Management file list not found, using module default(if there is).'
        for item in self.ScannerList:
            item.Url = self.Url
            item.Threads = int(self.Threads)
            item.Thread = int(self.Threads)
            item.UsernameFile = self.UsernameFile
            item.PasswordFile = self.PasswordFile
            item.UserPassFile = self.UserPassFile
            item.UserpassFile = self.UserPassFile
            if item == self.FTPBruteforcer:
                item.Port = self.FTPPort
            elif item == self.SSHPasswordScanner:
                item.Port = self.SSHPort
            elif item == self.SensitiveFileScanner:
                item.SensitiveFileList = self.SensitiveFileList
            elif item == self.AdminFetcher:
                item.AdminPageList = self.ManagementFileList
        pass


    def ServiceScanTask(self):
        self.ServiceScan = True
        print '[*] Starting service scan.'
        PortScannerThread = raw_input('[*] Provide port scanner thread to continue: ')
        if not PortScannerThread.isdigit():
            print '[!] Thread error, Require int value.'
            print '[*] Setting thread to 25.'
            self.PortChecker.Thread = 25
        else:
            self.PortChecker.Thread = int(PortScannerThread)
        self.PortChecker.Scan()
        self.OpenPortList = []
        for item in self.PortChecker.PortList:
            self.OpenPortList.append(item[0])
        SSHScanFlag = False
        FTPScanFlag = False
        if self.SSHPasswordScanner in self.ScannerList:
            SSHScanFlag = True
            if self.SSHPort not in self.OpenPortList:
                print '[!] SSH Port of target seems closed. Please provide new port or c to cancel SSH scan.'
                SSHPort = raw_input('[*] Please provide port or c to cancel: ')
                if 'c' in SSHPort:
                    SSHScanFlag = False
                    pass
                else:
                    if not SSHPort.isdigit():
                        print '[!] Port error, Require int value.'
                        print '[*] Setting default port to 22.'
                        self.SSHPasswordScanner.Port = 22
                    else:
                        self.SSHPasswordScanner.Port = int(SSHPort)
            else:
                pass
        self.PrintHandler.Mute()
        if SSHScanFlag:
            SSHIdentifyList = self.SSHPasswordScanner.Scan()
        else:
            SSHIdentifyList = []
        self.PrintHandler.Resume()
        if self.FTPBruteforcer in self.ScannerList:
            FTPScanFlag = True
            if self.FTPPort not in self.OpenPortList:
                print '[!] FTP port of target seems closed. Please provide new port or c to cancel FTP scan.'
                FTPPort = raw_input('[*] Please provide port or c to cancel: ')
                if 'c' in FTPPort:
                    FTPScanFlag = False
                else:
                    if not FTPPort.isdigit():
                        print '[!] Port error, Require int value.'
                        print '[*] Setting default port to 21.'
                        self.FTPBruteforcer.port = 21
                    else:
                        self.FTPBruteforcer.port = int(self.FTPPort)
        self.PrintHandler.Mute()
        if FTPScanFlag:
            FTPIdentifyList = self.FTPBruteforcer.Scan()
        else:
            FTPIdentifyList = []
        self.ServiceScan = False
        print '[*] Scan completed.'
        if SSHIdentifyList:
            print '[+] %i SSH Identify found.' %(len(SSHIdentifyList))
            print '[*] Incoming Identify'
            for item in SSHIdentifyList:
                print ' |    %s: %s' %(item[0], item[1])
            print '[*] Identify output completed.'
        if FTPIdentifyList:
            print '[+] %i FTP Identify found.' %(len(FTPIdentifyList))
            print '[*] Incoming Identify.'
            for item in FTPIdentifyList:
                print ' |    %s: %s' %(item.split(':')[0], item.split(':')[1])
            print '[*] Identify output completed.'
        print '[*] Service scan completed.'


    def WebScanTask(self):
        pass
