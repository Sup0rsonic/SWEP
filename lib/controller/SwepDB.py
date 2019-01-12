import lib.db.db
import ExploitHandler
import ScannerHandler

# SWEPdb functions lib.
# Replace should be like 'database sessions load', 'database exploit update', 'database hosts load' stuff.

class SWEPdb(): # Move database function to SWEPdb
    def __init__(self):
        self.Database = lib.db.db.DBHandler()
        self.ExploitLoader = ExploitHandler.ExploitHandler()
        self.ScannerLoader = ScannerHandler.ScannerHandler()
        pass


    def init(self): # Initalize database
        pass


    def update(self): # Update exploit
        pass


    def ExploitUpdate(self):
        ExploitNameList = []
        ExploitList = self.ExploitLoader.LoadExploit()
        for item in ExploitList:
            if not item:
                continue
            ExploitFile = {item['name']: item['description']}
            if ExploitFile not in ExploitNameList:
                ExploitNameList.append(ExploitFile)
        counter = 0
        for item in ExploitNameList:
            try:
                self.Database.Execute('INSERT OR REPLACE INTO exploit VALUES("%s", "%s")' %(item.keys()[0], item[item.keys()[0]]))
                counter += 1
            except Exception, e:
                print '[!] Failed to update an exploit: %s' %(str(e))
        print '[+] Exploit update completed, %s exploit(s) added.' %(str(counter))


    def ScannerUpdate(self):
        ScannerInfoList = []
        ScannerList = self.ScannerLoader.LoadScanner()
        try:
            for item in ScannerList:
                if not item:
                    pass
                if item not in ScannerInfoList:
                    ScannerInfoList.append(item)
            Counter = 0
            try:
                for item in ScannerInfoList:
                    self.Database.Execute('INSERT OR REPLACE INTO scanner VALUES("%s", "%s", "%s")' %(item['name'], item['description'], item['path']))
                    Counter += 1
            except Exception, e:
                print '[!] Error updating a scanner: %s' %(str(e))
                pass
        except Exception, e:
            print '[!] Failed to update scanner: %s' %(str(e))
            return
        print '[+] Scanner update completed, %s scanner(s) added' %(str(Counter))
        return

