import sys
import os
import json
import random
import getpass


# Banner list. I'm wondering about WHY I WILL WRITE THIS SH*T?
# AND I HATE COLORS
# But I got to do this.


class BannerLoader():
    def __init__(self):
        self.path = os.path.dirname(os.path.abspath(__file__))
        self.LoadBanner()


    def LoadBanner(self):
        try:
            self.BannerDict = []
            self.BannerList = json.load(open('%s/../BannerList.json' %(self.path)))['banner']
        except Exception, e:
            self.BannerList = None
            return
        for item in self.BannerList:
            self.BannerDict.append(item)


    def ShowBanner(self):
        if self.BannerList:
            print self.BannerList[random.randint(0, len(self.BannerList)-1)]
        self.PrintText()


    def PrintText(self):
        print '+--------------------------------------------------+'
        print '| SWEP - SWEP the open-Source Web Exploit Project  |'
        print '| Version 1.0 alpha development                    |'
        print '| Welcome, %s|' %(getpass.getuser()).ljust(40, ' ')
        print '+--------------------------------------------------+'