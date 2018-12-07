import json
import os
import re

class FingerprintLoader():
    def __init__(self):
        self.CmsList = {}
        self.CmsVersionList = {}
        if self._CheckFingerprint():
            exit()


    def _CheckFingerprint(self):
        if os.path.isdir('./cms./'):
            pass
        else:
            return 1
        if os.path.isdir('./cms/version'):
            pass
        else:
            return 2
        return 0


    def LoadCmsNameFingerprint(self,lang): # Loads fingerprint to confirm cms, then version.
        try:
            for filename in os.listdir('./cms/%s/' %(lang)):
                if filename.endswith('.json'):
                    CmsJson = json.load(open('./cms/%s/%s' %(filename)))
                    CmsName = re.sub('\.json','',filename)
                    self.CmsList[CmsName] = CmsJson
        except Exception, e:
            print '[!] Load CMS file failed: %s' %(e)
            pass
        print '[*] CMS load complete.'
        print '[*] Loaded %s CMS(s)' %(str(len(self.CmsList)))
        return self.CmsList


    def LoadCmsVersionFingerprint(self,cms): # Loads fingerprint to confirm cms version
        try:
            for filename in os.listdir('./cms/version/%s' %(cms)):
                if filename.endswith('.json'):
                    VersionJson = json.load(open('./cms/version/%s/%s' %(cms,filename)))
                    self.CmsVersionList[filename] = VersionJson
        except Exception, e:
            print '[!] Load CMS version file failed: %s' %(e)
            pass
        print '[*] CMS load complete.'
        print '[*] Total %s version(s)' %(str(len(self.CmsVersionList)))
        return self.CmsVersionList


