import lib.exp
import importlib
import os


class ExploitLoader(): # List dir, Get file from dir, Check name from db
    def __init__(self):
        self.Threads = 30 # Threads. Maybe unnecessary.
        self.ExploitList = [] # Exploits
        self.dir = os.path.abspath(os.path.dirname(__file__))
        self.ExploitDir = self.dir + '/../exp/'
        self.ExploitFileList =  os.listdir(self.ExploitDir)
        pass


    def GetExploitList(self):
        ExploitFileList = []
        for item in self.ExploitFileList:
            try:
                if str(item).endswith('.py') and str(item) not in ExploitFileList and item != '__init__.py':
                    ExploitFileList.append(str(item))
            except Exception ,e:
                print '[!] Error loading an exploit to list: %s' %(str(e))
        return  ExploitFileList


    def LoadExploit(self):
        ExploitList = self.GetExploitList()
        print '[+] Exploit list load success, total %s exploit(s).' %(str(len(ExploitList)))
        for item in ExploitList:
            self._ExploitLoader(item)
        print '[+] Exploit load success.'
        return self.ExploitList


    def _ExploitLoader(self, exploit):
        try:
            name = 'lib.exp.%s' %(exploit.rstrip('.py'))
            Exploit = importlib.import_module(name)
            self.ExploitList.append(Exploit.info())
            del Exploit
            return self.ExploitList
        except Exception, e:
            print '[!] Error loading an exploit info: %s '%(str(e))
        return

