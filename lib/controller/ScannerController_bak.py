import lib.scanner.ManagementScanner.ManagementScanner
import lib.scanner.SQLInjectionScanner.Scanner
import lib.scanner.FTPPasswordScanner.FTPPasswordScanner
import os
import sys


class ScannerController():
    def __init__(self):
        self.url = None
        self.Host = None
        self.Port = None
        self.Protocol = None
        self.Threads = None
        self.Scanner = None
        self.path = os.path.abspath(__file__)
        pass


    def CheckArgument(self, command):
        if command == '':
            return
        RawCommandDict = command.split(' ', 1)
        CommandDict = []
        for item in RawCommandDict:
            CommandDict.append(str(item).strip(' '))
        if len(CommandDict) == 0:
            return
        if CommandDict[0] == 'scan':
            self.Scan()
        elif CommandDict[0] == 'set':
            if len(CommandDict) != 2:
                print '[*] SWEP Scanner: set *args\n    Examples: scanner set arg value'
                return
            self.set(CommandDict[1])
        elif CommandDict[0] == 'unset':
            if len(CommandDict) != 2:
                print '[*] SWEP Scanner: unset *args\n    Examples scanner unset arg'
                return
        elif CommandDict[0] == 'info':
            self.info()
        elif CommandDict[0] == 'help':
            if len(CommandDict) != 2:
                self.help()
            else:
                self.help(CommandDict[1])
        elif CommandDict[0] == 'interactive':
            print '[*] SWEP Scanner: Starting Interactive mode, Ctrl+D to exit'
            self.Interactive()
        elif CommandDict[0] == 'load':
            if len(CommandDict) != 2:
                print '[*] SWEP Scanner: load [name]'
                return
            self.load(CommandDict[1])
        elif CommandDict[0] == 'unload':
            self.unload()
        elif CommandDict[0] == 'cd':
            if len(CommandDict) != 2:
                self._cd(self.path)
            else:
                self._cd(CommandDict[1])
        else:
            os.system(command)
        return


    def _cd(self, path):
        try:
            os.chdir(path)
        except Exception, e:
            print '[!] Failed to change dir: %s' %(str(e))
        return


    def Scan(self):
        try:
            Response = self.Scanner.Scan()
        except Exception, e:
            print '[!] Failed to starting scan: %s' %(str(e))
        return


    def set(self, args):
        if not self.Scanner:
            print '[!] Error: Scanner not specified.'
            return
        try:
            ArgumentDict = args.split(' ')
            self.Scanner.__dict__[ArgumentDict[0]] = ArgumentDict[1]
        except Exception, e:
            print '[!] Failed to set value: %s' %(str(e))
        return


    def unset(self, args):
        try:
            ArgumentDict = args.strip(' ').split(' ')
            self.Scanner.__dict__[ArgumentDict[0]] = None
        except Exception,e :
            print '[!] Failed to unset: %s' %(str(e))
        return


    def info(self):
        self.Scanner.info()
        return


    def Interactive(self):
        while True:
            if not self.Scanner:
                ScannerName = 'None'
            else:
                ScannerName = self.Scanner.Name
            try:
                cmd = raw_input('SCANNER(%s):%s-$ ' %(str(ScannerName), str(os.getcwd())))
                RawCommandDict = cmd.split(' ', 1)
                CommandDict = []
                for item in RawCommandDict:
                    if item.strip(' ') == '':
                        continue
                    CommandDict.append(item.strip())
                if len(CommandDict) == 0:
                    continue
                if CommandDict[0] == 'help':
                    self.help()
                elif CommandDict[0] == 'set':
                    if len(CommandDict) != 2:
                        print '[*] SWEP Scanner Interactive: set *args\n    Examples: set arg value'
                        continue
                    self.set(CommandDict[1])
                elif CommandDict[0] == 'unset':
                    if len(CommandDict) != 2:
                        print '[*] SWEP Scanner Interactive: set *args\n    Examples: unset arg'
                        continue
                    self.unset(CommandDict[1])
                elif CommandDict[0] == 'load':
                    if len(CommandDict) != 2:
                        print '[*] SWEP Scanner Interactive: load [sql ftp admin]'
                        continue
                    self.load(CommandDict[1])
                elif CommandDict[0] == 'info':
                    self.info()
                elif CommandDict[0] == 'unload':
                    self.unload()
                elif CommandDict[0] == 'scan':
                    self.Scan()
                elif CommandDict[0] == 'cd':
                    if len(CommandDict) != 2:
                        self._cd(self.path)
                    else:
                        self._cd(CommandDict[1].strip(' '))
                else:
                    os.system(cmd)
            except KeyboardInterrupt:
                print '[*] Press Ctrl+D to exit.'
            except EOFError:
                print '[*] Exit.'



    def help(self, *name):
        HelpDict = {
            'set': 'Set value of a parameter\nUsage: set *args\nExample: set arg value',
            'unset': 'Delete value of specified parameter\nUsage: unset value',
            'load': 'Load a scanner module.\nUsage: load [module]\nType \'module\' to show modules.',
            'unload': 'Unload specified module.',
            'info': 'Show module info.',
            'scan': 'Scan site.',
            'interactive': 'Enter interactive mode.',
            'help': 'Print help.'
        }
        ModuleDict = {
            'sql': 'SQL Injection Check Module.',
            'ftp': 'FTP Password bruteforce module.',
            'admin': 'Management page bruteforce module'
        }
        if name:
            if name in HelpDict.keys():
                print HelpDict[name]
                return
            else:
                pass
        print 'COMMAND' + ' ' * 40 + 'DESCRIPTION'
        print '=' * 7 + ' ' * 41 + '=' * 11
        for arg in HelpDict.keys():
            print arg.ljust(47, ' ') + HelpDict[arg]
        print '\n'*3
        print 'MODULE' + ' ' * 20 + 'INFORMATION'
        print '=' * 6 + ' ' * 21 + '=' * 11
        for arg in ModuleDict.keys():
            print arg.ljust(27, ' ') + ModuleDict[arg]
        return



    def load(self, mode):
        try:
            if mode == 'sql':
                self.Scanner = lib.scanner.SQLInjectionScanner.Scanner.SQLInjectionScanner()
            elif mode == 'ftp':
                self.Scanner = lib.scanner.FTPPasswordScanner.FTPPasswordScanner.FTPPasswordScanner()
            elif mode == 'admin':
                self.Scanner = lib.scanner.ManagementScanner.ManagementScanner.ManagementScanner()
            else:
                print '[!] SWEP scanner modules: load [sql ftp admin] *args'
                return
        except Exception, e:
            print '[!] Failed to load module: %s' %(str(e))
        return


    def unload(self):
        try:
            if self.Scanner:
                del self.Scanner
        except Exception, e:
            print '[!] Error unloading module: %s' %(str(e))
        return


def test():
    Controller = ScannerController()
    Controller.Interactive()

test()