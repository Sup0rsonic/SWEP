import os
import lib.db.db
import lib.controller.ScannerLoader
import lib.controller.DatabaseHandler
import json


class ScannerHandler():
    def __init__(self):
        self.ScannerList = None
        self.path = os.path.abspath(__file__)
        self.dir = os.path.dirname(self.path)
        self.JsonFile = '%s../../scanner/scanner.json' # Legacy code for previous version scanner loader.
        self.ScannerLoader = lib.controller.ScannerLoader.ScannerLoader()
        pass


    def LoadJson(self):
        try:
            if not os.path.isfile(self.JsonFile):
                print '[*] Json file not found.'
                return None
            try:
                self.ScannerList = json.load(open(self.JsonFile))
                if not self.ScannerList:
                    print '[!] Failed to load json.'
            except Exception ,e:
                print '[!] Failed to load json file: %s' %(str(e))
        except Exception, e:
            print '[!] Failed to load json: %s' %(str(e))
        return self.ScannerList


    def LoadScanner(self):
        self.ScannerList = self.ScannerLoader.LoadScanner()
        if not self.ScannerList:
            self.LoadJson()
        return self.ScannerList


def test():
    handler = ScannerHandler()
    handler.LoadScanner()
