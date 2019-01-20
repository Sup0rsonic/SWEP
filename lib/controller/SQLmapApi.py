import lib.config
import subprocess
import os
import sys


class SQLMapApi():
    def __init__(self):
        pass


    def VerifySQLiFromSQLmap(self, UrlList, mode):
        if not list:
            print '[!] No url found.'
            return
        if mode == 'call':
            if not lib.config.SQLmapPath:
                print '[!] SQLmap path not specified.'
                return
            fp = open('SQLmapUrlList', 'w+')
            for item in UrlList:
                fp.write(item)
                fp.write('\n')
            subprocess.Popen('python %s -m SQLmapUrlList -a --dump-all', shell=True)
            return
        elif mode =='api':
            pass
        else:
            pass

