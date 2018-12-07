import json
import os


class FingerprintLoader():
    def __init__(self):
        self.Language = None
        self.CMS = None
        self.DB = None
        self.WAF = None
        self.path = os.path.dirname(os.path.abspath(__file__))
        pass


    def LoadSiteFingerprint(self):
        try:
            if self.Language == 'other':
                SiteFingerprint = {u'hashes':[], u'pages':[], u'headers':[]}
                for item in ['php', 'dotnet', 'jsp', 'other']:
                    LangFingerprint = json.load(open('%s/db/%s.json' %(self.path, item)))
                    for item in LangFingerprint.keys():
                        if item == u'type':
                            continue
                        for val in LangFingerprint[item]:
                            SiteFingerprint[item].append(val)
                return SiteFingerprint
            SiteFingerprint = json.load(open('%s/db/%s.json' %(self.path, self.Language)))
        except Exception ,e:
            print '[!] Failed to load fingerprint for language %s: %s' % (self.Language, e)
            SiteFingerprint = None
        return SiteFingerprint


    def LoadCmsVerionFingerprint(self):
        if not self.CMS:
            print '[!] CMS not specified.'
            return
        try:
            RawJson = json.load(open('%s/cms/version/%s/versions.json'))
        except Exception,e :
            print '[!] Failed to load json: %s' %(str(e))
            return
        return RawJson


    def LoadWafFingerprint(self):
        try:
            WafFingerprint = json.load(open('%s/db/waf.json' %(self.path)))
        except Exception, e:
            print '[!] Failed to load WAF fingerprint: %s' %(str(e))
            WafFingerprint = None
        return WafFingerprint


    def LoadDatabaseVersion(self):
        pass


