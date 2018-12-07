import re
import os
import SiteController
import HelpController
import FunctionLib
import ScannerController
import DatabaseHandler
import ExploitLoader


# Command Handler. Load at init

class CommandHandler():
    def __init__(self):
        self.site = None
        self.module = None
        self.dir = self.basedir = os.getcwd()
        self.path = os.path.abspath(__file__)
        self.modulename = None
        self.HelpController = HelpController.HelpController()
        self.Scanner = ScannerController.ScannerController()
        self.Exploit = None
        self.DatabaseHandler = DatabaseHandler.DatabaseHandler()
        self.ExploitLoader = ExploitLoader.ExploitHandler()
        try:
            os.chdir(self.dir)
        except:
            pass
        pass

    def _GetCommand(self):
        while True:
            cmd = raw_input('swep:%s(%s):%s~$ '%(str(self.site.Name if self.site else None),str(self.modulename),str(self.dir)))
            if cmd != '':
                self.ReadCommand(str(cmd))

    def ReadCommand(self,cmd):
        CommandDict = re.split(' ',cmd,1)
        if len(CommandDict) == 0:
            CommandDict[1] = ''
        if CommandDict[0] == 'site':
            if self._ParmCheck('site', CommandDict):
                return
            self._Site(CommandDict[1])
        else:
            if CommandDict[0] == 'search':
                if self._ParmCheck('search', CommandDict):
                    return
                self.Search(CommandDict[1])
            elif CommandDict[0] == 'use':
                if self._ParmCheck('use', CommandDict):
                    return
                self.use(str(CommandDict[1]))
            elif CommandDict[0] == 'back':
                self.back()
            elif CommandDict[0] == 'check':
                if self._ParmCheck('check', CommandDict):
                    return
                self.check(CommandDict[1])
            elif CommandDict[0] == 'load':
                if self._ParmCheck('load', CommandDict):
                    return
                self.load(CommandDict[1])
            elif CommandDict[0] == 'unload':
                self.unload()
            elif CommandDict[0] == 'whois':
                if self._ParmCheck('whois', CommandDict):
                    return
                self.whois(CommandDict[1])
            elif CommandDict[0] == 'subnet':
                if self._ParmCheck('subnet', CommandDict):
                    return
                ParmDict = re.split(' ', CommandDict[1])
                if len(ParmDict) != 2:
                    print '[*] Subnet mode not specified, Using C mode.'
                    self.subnet(ParmDict[0], 'c')
                    return
                self.subnet(ParmDict[0],ParmDict[1])
            elif CommandDict[0] == 'addr':
                if self._ParmCheck('addr', CommandDict):
                    return
                self.getAddr(CommandDict[1])
            elif CommandDict[0] == 'set':
                if self._ParmCheck('set', CommandDict) or len(CommandDict) != 3:
                    return
                ParmDict = re.split(' ', CommandDict[1])
                self.set(ParmDict[0], ParmDict[1])
            elif CommandDict[0] == 'unset':
                if self._ParmCheck('unset', CommandDict):
                    return
                self.unset(CommandDict[1])
            elif CommandDict[0] == 'exploit':
                self.exploit()
            elif CommandDict[0] == 'fingerprint':
                if self._ParmCheck('fingerprint', CommandDict):
                    return
                self.Fingerprint(CommandDict[1])
            elif CommandDict[0] == 'grab':
                if self._ParmCheck('grab', CommandDict):
                    return
                self.grab(CommandDict[1])
            elif CommandDict[0] == 'info':
                self.info()
            elif CommandDict[0] == 'domain':
                if self._ParmCheck('domain', CommandDict):
                    return
                self.domain(CommandDict[1])
            elif CommandDict[0] == 'cd':
                if len(CommandDict) == 1:
                    self._cd(self.basedir)
                else:
                    self._cd(CommandDict[1])
            elif CommandDict[0] == 'scanner':
                if self._ParmCheck('scanner', CommandDict):
                    return
                self.HelpController.help('scanner')
                self.Scan(CommandDict[1])
            elif CommandDict[0] == 'database':
                if len(CommandDict) < 2:
                    self.HelpController.help('database')
                    return
                self.Database(CommandDict[1])
            elif CommandDict[0] == 'help':
                self.HelpController.help('help')
            else:
                self._System(CommandDict[0])
        return

    def _ParmCheck(self, module, parm):
        if len(parm) != 2:
            self.HelpController.usage(module)
            return 1
        else:
            return 0

    def _Site(self,parm): # site xxx xxx
        CommandDict = re.split(' ',parm)
        if CommandDict[0] == 'help':
            self.HelpController.help('site')
        if not self.site:
            print '[!] Site not specified.'
            return
        if CommandDict[0] == 'whois':
            self.site.Whois()
        elif CommandDict[0] == 'subnet':
            if len(CommandDict) != 2:
                print '[*] Please specify mode.'
                return
            self.subnet(self.site.url, CommandDict[1])
        elif CommandDict[0] == 'address':
            self.getAddr(self.site.url)
        elif CommandDict[0] == 'fingerprint':
            self.Fingerprint(self.site.url)
        elif CommandDict[0] == 'grab':
            self.grab(self.site)
        elif CommandDict[0] == 'exploit':
            if not self.exploit:
                print '[!] Exploit not select.'
            self.exploit()
        elif CommandDict[0] == 'domain':
            self.site.GetSite()
            return
        elif CommandDict[0] == 'check':
            if len(CommandDict) != 2:
                print '[*] Please specify mode.'
                return
            self._CheckSiteInformation(CommandDict[1])
        else:
            self.HelpController.help('check')
        return


    def _CheckSiteInformation(self, mode):
        if mode in ['cms', 'version', 'waf', 'language', 'db', 'system']:
            self.site.CheckInformation(mode)
        elif mode == 'update':
            self.site.information = { 'system': None, 'db': None, 'waf': None}
            self.site.cms = {'cms': None, 'version': None, 'site': None}
        elif mode == 'help':
            self.HelpController.help('check')
        else:
            print '[*] SWEP Site Session Checker: site check [cms version waf language db update system help] *args'
        return


    def session(self, action):
        pass


    def Database(self, cmd):
        CommandList = cmd.split(' ')
        if not len(CommandList):
            self.HelpController.usage('database')
            return
        elif CommandList[0] == 'search':
            try:
                if len(CommandList) != 2:
                    self.HelpController.usage('db_search')
                    return
                self.DatabaseHandler.SearchHost(CommandList[1])
            except Exception, e:
                print '[!] Failed to search host: %s' %(str(e))
            return
        elif CommandList[0] == 'load':
            if self.site:
                if raw_input('[*] This action will destroy current site session. Continue? (Y/N)').upper() != 'Y':
                    return
            try:
                if len(CommandList) < 2:
                    self.HelpController.usage('db_load')
                    return
                RawSession = self.DatabaseHandler.LoadHost(CommandList[1])[0][2]
                self.site = self.DatabaseHandler.Unseralize(RawSession)
                print '[+] Site load success.'
            except Exception, e:
                print '[!] Failed to load site: %s' %(str(e))
            return
        elif CommandList[0] == 'insert':
            if not self.site:
                print '[!] Site not specified.'
                return
            try:
                RawSession = self.DatabaseHandler.Serialize(self.site)
                self.DatabaseHandler.InsertHost((self.site.url ,RawSession))
                print '[+] Site saved.'
            except Exception, e:
                print '[!] Failed to save site: %s' %(str(e))
            return
        elif CommandList[0] == 'update':
            if not self.site:
                print '[!] Site not specified.'
                return
            try:
                if len(CommandList) != 2:
                    self.HelpController.usage('db_update')
                    return
                self.DatabaseHandler.UpdateHost(CommandList[1], self.site)
            except Exception, e:
                print '[!] Failed to update site: %s' %(str(e))
            return
        elif CommandList[0] == 'delete':
            if len(CommandList) != 2:
                self.HelpController.usage('db_delete')
                return
            if raw_input('[!] Are you sure you want to DELETE a site?\nThis CAN\'T be undone. (Y/N)').upper() != 'Y':
                return
            try:
                self.DatabaseHandler.DeleteHost(CommandList[1])
                print '[+] Site delete complete.'
            except Exception, e:
                print '[!] Failed to delete host: %s' %(str(e))
            return
        elif CommandList[0] == 'help':
            self.HelpController.help('database')
        else:
            self.HelpController.usage('database')
            return



    def _System(self,cmd): # Execute in shell
        try:
            os.system(cmd)
        except:
            pass
        return

    def _cd(self,dir): # Change dir
        try:
            os.chdir(str(dir))
            self.dir = os.getcwd()
        except:
            pass
        return

    def Search_back(self,name): # Search module name - Backup
        list = []
        for root,dirs,file in os.walk(self.basedir + '/lib/exp'):
            for i in file:
                list.append(str(i))
        for i in list:
            if i.find(name) != -1:
                        print i.rstrip('.py')


    def Search(self, module):
        self.ExploitLoader.FindExp(module)
        return


    def use(self,module): # Load module
        try:
            self.module = self.ExploitLoader.FetchExp(module)
            self.Exploit = self.module.exploit()
            if self.Exploit:
                self.modulename = module
            else:
                self.modulename = None
        except Exception, e:
            print '[!] Failed to import module %s: %s' %(str(module),str(e))
        return


    def back(self): # Unload module
        try:
            self.module = None
            self.Exploit = None
            self.modulename = None
        except Exception,e:
            print '[!] Failed to unload module %s: %s' %(str(self.module),str(e))
        return

    def check(self, site): # Check site
        Parm = re.split(' ', site)
        if Parm[0] not in ['site', 'waf', 'cms', 'version', 'db', 'language site'] or len(Parm) == 1:
            print '[*] SWEP Check: check [waf cms language db version site] site'
            return
        try:
            FunctionLib.Fingerprint(Parm[1], Parm[0])
        except Exception, e:
            print '[!] Error checking site %s: %s' %(str(Parm[1]), e)
        return


    def load(self, site): # Specify site
        self.site = SiteController.site()
        self.site.Name = site
        self.site.FingerprintIdentifier.url = site
        self.site.url = str(site)
        return

    def unload(self): # Unload site
        self.site = None
        return

    def whois(self, site): # Query whois
        FunctionLib.Whois(site)
        pass

    def subnet(self, site, type): # Query subnet
        FunctionLib.Subnet(site,type)
        pass

    def getAddr(self, site): # Get target addres
        FunctionLib.GetAddr(site)
        pass

    def searchDB(self, keywd): # Search host from DB
        pass


    def loadDB(self, id): # Load host from DB
        pass

    def attatchDB(self, site): # Attach current to DB
        pass

    def delDB(self, site): # Del host from DB
        pass

    def insertDB(self, site): # Insert into DB
        pass

    def set(self, parameter, value): # Set value
        if not self.Exploit:
            print '[!] Module not loaded. '
            return
        self.Exploit.param[str(parameter)] = value
        print '[*] %s -> %s' %(str(parameter),str(value))

    def unset(self, parameter): # Unset value
        if not self.Exploit:
            print '[!] Module not loaded.'
            return
        self.Exploit.param[str(parameter)] = None
        pass

    def exploit(self): # Exploit with exploit
        try:
            self.Exploit.exploit()
        except AttributeError:
            print '[!] Please specify module.'
        except IndexError:
            print '[!] Please specify target.'
        except Exception, e:
            print '[!] Error: %s' %(str(e))
        pass

    def Fingerprint(self, site): # Check fingerprint
        try:
            print '[*] Fingerprint function is deprecated, please use check function instead.'
            FunctionLib.Fingerprint(site, 'cms')
        except:
            self.HelpController.usage('fingerprint')
        return


    def domain(self, site):
        addr = FunctionLib.GetSameIP(site)
        return


    def grab(self, site): # Get homepage
        try:
            FunctionLib.GetPage(site)
        except:
            self.HelpController.usage('grab')
        return

    def Scan(self, command):
        self.Scanner.InterpretCommand(command)
        return


    def info(self):
        if not self.Exploit:
            print '[*] Exploit not specified.'
            return
        try:
            self.Exploit.info()
        except Exception, e:
            print '[!] Failed to load info: %s.' %(str(e))
        return

