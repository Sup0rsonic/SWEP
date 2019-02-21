import os
import sys
import ModuleHandler

# Main handler. This will process most of function and some stuff.


class MainHandler():
    def __init__(self):
        self.Url = None
        self.ModuleHandler = ModuleHandler.ModuleHandler()
        self.Threads = None
        pass


    def Set(self, module, arg, val):
        if not module:
            for item in self.ModuleHandler.ScannerList:
                self.ModuleHandler.ScannerList[item]['item'].__dict__[arg] = val
        else:
            if module not in self.ModuleHandler.ScannerList.keys():
                self.PrintMenu('[!] Scanner not found.')
                return
            self.ModuleHandler.ScannerList[module]['item'].__dict__[arg] = val
        self.PrintMenu()
        return


    def Unset(self, module, arg):
        if not module:
            for item in self.ModuleHandler.ScannerList:
                self.ModuleHandler.ScannerList[item]['item'].__dict__[arg] = None
        else:
            if module not in self.ModuleHandler.ScannerList.keys():
                self.PrintMenu('[!] Scanner %s not found.')
                return
            self.ModuleHandler.ScannerList[module]['item'].__dict__[arg] = None
        self.PrintMenu()
        return


    def Switch(self, module ,stat):
        if module not in self.ModuleHandler.ScannerList.keys():
            self.PrintMenu('[*] Task not found.')
            return
        if stat.upper() == 'ON':
            self.ModuleHandler.ScannerList[module]['stat'] = True
        elif stat.upper == 'OFF':
            self.ModuleHandler.ScannerList[module]['stat'] = False
        else:
            self.PrintMenu('[!] Invalid mode.')
            return
        self.PrintMenu()
        return


    def Scan(self):
        self.ModuleHandler.Scan()
        pass


    def GetResponse(self):
        if self.ModuleHandler.ScannerList['sql']['stat']:
            if len(self.ModuleHandler.ScannerList['sql']['item'].UrlList):
                print '[*] %i URL(s) seems vulnerable to SQL Injection.' %(len(self.ModuleHandler.ScannerList['sql']['item'].UrlList))
                print '[*] Incoming URL: '
                for item in self.ModuleHandler.ScannerList['sql']['item'].UrlList:
                    print '  |    %s' %(item)
                print '[*] SQL Injection URL output completed.'
        if self.ModuleHandler.ScannerList['xss']['stat']:
            if len(self.ModuleHandler.ScannerList['xss']['item'].UrlList):
                print '[*] %i URL(s) seems vulnerable to XSS.' %(len(self.ModuleHandler.ScannerList['xss']['item'].UrlList))
                print '[*] Incoming URL:'
                for item in self.ModuleHandler.ScannerList['xss']['item'].UrlList:
                    print '  |    %s' %(item)
                print '[*] XSS URL output completed.'
        if self.ModuleHandler.ScannerList['admin']['stat']:
            if len(self.ModuleHandler.ScannerList['admin']['item'].UrlList):
                print '[*] %i potential admin pages found.' %(len(self.ModuleHandler.ScannerList['admin']['item'].UrlList))
                print 'Incoming URL: '
                for item in self.ModuleHandler.ScannerList['admin']['item'].UrlList:
                    print item
                print '[*] Admin URL output completed.'
        if self.ModuleHandler.ScannerList['file']['stat']:
            if len(self.ModuleHandler.ScannerList['file']['item'].UrlList):
                print '[*] %i sensitive file(s) found.' %(len(self.ModuleHandler.ScannerList['file']['item'].UrlList))
                print '[*] Incoming sensitive file list.'
                for item in self.ModuleHandler.ScannerList['file']['item'].UrlList:
                    print '  |    %s' %(item)
                print '[*] Sensitive File output completed.'
        if self.ModuleHandler.ScannerList['ftp']['stat']:
            if len(self.ModuleHandler.ScannerList['ftp']['item'].UserPassList):
                print '[*] %i FTP Identify found.' %(len(self.ModuleHandler.ScannerList['ftp']['item'].UserPassList))
                for item in self.ModuleHandler.ScannerList['ftp']['item'].UserPassList:
                    print '  |    %s' %(item)
        if self.ModuleHandler.ScannerList['ssh']['stat']:
            if len(self.ModuleHandler.ScannerList['ssh']['item'].IdentifyList):
                print '[*] %i SSH Identify found.' %(len(self.ModuleHandler.ScannerList['ssh']['item'].IdentifyList))
                for item in self.ModuleHandler.ScannerList['ssh']['item'].IdentifyList:
                    print '  |    %s:%s' %(item[0], item[1])
        print '[*] Identify output completed.'
        return  0


    def ShowInformation(self):
        pass


    def PrintMenu(self, *info):
        self.ShowMenu()
        if info:
            for item in info:
                print item


    def ShowMenu(self):
        os.system('cls||clear')
        print '[SWEP Intruder]'
        print
        print '---Functions flag---'
        print '[+] WEB Scanner' if self.ModuleHandler.WebScanFlag else '[-] WEB Scanner'
        print '[+] Service Scanner' if self.ModuleHandler.ServiceScanFlag else '[-] Service Scanner'
        '--Modules Status--'
        print 'Scanner      Description         Status'
        print '-------      -----------         ------'
        for item in self.ModuleHandler.ScannerList:
            print '%s%s%s' %(item.ljust(13, ' '), self.ModuleHandler.ScannerList[item]['name'].ljust(20, ' '), 'ON' if self.ModuleHandler.ScannerList[item]['stat'] else 'OFF')
        pass

