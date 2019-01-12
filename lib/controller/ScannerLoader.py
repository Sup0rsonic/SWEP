import os
import importlib


# Scanner load module.
# This SHOULD be only comment. God cares - it's easy to read =D
# So good luck if there's a bug.

class ScannerLoader():
    def __init__(self):
        self.dir = os.path.dirname(os.path.abspath(__file__))
        self.ScannerDir = self.dir + '/../scanner/'
        self.ScannerList = []


    def GetScannerList(self):
        if not os.path.isdir(self.ScannerDir):
            print '[!] Failed to load scanner: dir not found.'
            return 0
        ScannerFileList = []
        for item in os.listdir(self.ScannerDir):
            if item.endswith('.py') and '__init__' not in item:
                ScannerFileList.append(item)
        return ScannerFileList


    def LoadScanner(self):
        ScannerFileList = self.GetScannerList()
        if ScannerFileList:
            print '[*] %s scanner(s) found.' %(len(ScannerFileList))
        else:
            print '[*] Warning: Scanner not found. Check your scanner dir.'
            return 0
        for item in ScannerFileList:
            self.GetScannerInformation(item)
        return self.ScannerList


    def GetScannerInformation(self, scanner):
        if not os.path.isfile(self.dir + '/../scanner/' + scanner):
            print '[*] Error loading scanner information: File not found.'
        try:
            ScannerName = 'lib.scanner.%s' % (str(scanner).strip('.py'))
            self.scanner = importlib.import_module(ScannerName)
            ScannerInformation = self.scanner.info()
            if not ScannerInformation:
                print '[!] Error: Scanner information not provided.'
            self.ScannerList.append(ScannerInformation)
        except Exception, e:
            print '[!] Failed to fetch scanner information: %s' % (str(e))
        return


def test():
    scanner = ScannerLoader()
    scanner.LoadScanner()
    print str(scanner.ScannerList)
