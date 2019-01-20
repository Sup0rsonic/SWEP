import lib.config
import subprocess
import os
import sys
sys.path.append(lib.config.SQLmapDir)
from sqlmap import *

# Development options.
# Todo: Remove after development
dev = True


class SQLMapApi():
    def __init__(self):
        self.SQLMapDir = lib.config.SQLmapDir
        if dev:
            self.SQLMapDir = '/usr/share/'
        if not os.path.isdir(self.SQLMapDir):
            print '[!] Invalid SQLmap Dir. Check your config.'
            return
        self.SqlmapPath = self.SQLMapDir + 'sqlmap.py'
        sys.path.append(self.SQLMapDir)
        pass


    def VerifySQLiFromSQLmap(self, UrlList, mode):
        if not list:
            print '[!] No url found.'
            return
        if mode == 'call':
            if not self.SqlmapPath:
                print '[!] SQLmap path not specified.'
                return
            fp = open('SQLmapUrlList', 'w+')
            for item in UrlList:
                fp.write(item)
                fp.write('\n')
            subprocess.Popen('python %s/sqlmap.py -m SQLmapUrlList -a --dump-all' %(self.SqlmapPath), shell=True)
            return
        elif mode =='api':
            pass
        else:
            pass


    # def Launch(self): # Copied from sqlmap, hope this will work
    #     # Store original command line options for possible later restoration
    #     sqlmap.cmdLineOptions.update(cmdLineParser().__dict__)
    #     sqlmap.initOptions(cmdLineOptions)
    #     sqlmap.conf.showTime = True
    #     pass # Print status
    #     sqlmap.init()


    def StartApi(self):
        sqlmapapi.main()


def test():
    api = SQLMapApi()

test()