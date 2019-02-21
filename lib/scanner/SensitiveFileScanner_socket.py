import socket
import os
import threading
import queue
import re
import ssl
import time


def info():
    info = {
        'name': 'filesocket',
        'path': 'SensitiveFileScanner_socket',
        'fullname': 'SWEP SENSITIVE FILE SCANNER WITH SOCKET',
        'description': 'A not very simple scanner',
        'parameters': {
            'Url': 'Target URL.',
            'Protocol': 'Protocol. Default: http',
            'Addr': 'Target IP address',
            'Port': 'Target port',
            'WordList': '(OPTIONAL) Sensitive File Wordlist',
            'Thread': '(OPTIONAL) Threads. Default: 10',
            'Timeout': '(OPTIONAL) Request timeout. Default: 3'
        },
        'author': 'BERACHERS security',
        'date': '2019-02-21'
    }
    return info


class Scanner():
    def __init__(self):
        self.Url = None
        self.Addr = None
        self.Port = 80
        self.Wordlist = ''
        self.Protocol = None
        self.TaskList = []
        self.Status = True
        self.UrlList = {}
        self.Time = 0
        self.Queue = queue.Queue()
        self.SensitiveFileList = None
        self.Path = os.path.dirname(os.path.abspath(__file__))
        self.WordlistDir = self.Path + '/../../WordLists/'
        self.Payload = ''
        self.Timeout = 3
        self.Threads = 10
        pass


    def Scan(self):
        try:
            self.StartScan()
        except KeyboardInterrupt:
            print '[*] User stop.'
        except Exception, e:
            print '[!] Failed fetching page: %s' %(str(e))
            return
        if not self.UrlList:
            print '[+] Scan completed, no file found.'
            return self.UrlList
        for item in self.UrlList.keys():
            print '[*] Status code: %s, %i URL(s) found,' % (item, len(self.UrlList[item]))
            for url in self.UrlList[item]:
                print '  |    Fetched: %s' % (url)
        print '[*] Fetch completed.'
        return self.UrlList


    def StartScan(self):
        print '[*] Initializing scanner.'
        if not self.Addr and not self.Url:
            print '[!] URL Not specified.'
            return
        if not str(self.Threads).isdigit():
            print '[!] Invalid thread count. Using 10 by default.'
            self.Threads = 10
        if not str(self.Timeout).isdigit():
            print '[!] Invalid timeout count. Using 3 by default.'
            self.Timeout = 3
        if ':' in self.Url:
            self.Url = self.Url.split(':')[0]
            self.Port = self.Url.split(':')[1]
        if not self.Protocol:
            print '[!] Invalid protocol. Using http by default.'
            self.Protocol = 'http'
        if not str(self.Port).isdigit():
            print '[!] Invalid port.'
            if self.Protocol == 'https':
                print '[*] Using 443 by your protocol option.'
                self.Port = 443
            else:
                print '[*] Using 80 by your protocol option.'
                self.Port = 80
        self.Threads = int(self.Threads)
        self.Timeout = int(self.Timeout)
        self.Port = int(self.Port)
        for item in self.LoadWordlist():
            self.Queue.put(item)
        print '[*] %i URL(s) loaded.' %(self.Queue.qsize())
        timer = threading.Thread(target=self._Timer)
        timer.setDaemon(True)
        checker = threading.Thread(target=self._ThreadChecker)
        checker.setDaemon(True)
        notifier = threading.Thread(target=self._TaskNotifier)
        notifier.setDaemon(True)
        print '[*] Now starting scan.'
        self.Status = True
        self.Time = 0
        timer.start()
        checker.start()
        notifier.start()
        while self.Queue.qsize():
            if len(self.TaskList) < self.Threads:
                thread = threading.Thread(target=self._Scanner, args=[self.Queue.get()])
                thread.start()
                self.TaskList.append(thread)
            if not self.Queue.qsize():
                print '[*] Scan completed, synchronizing threads.'
                for item in self.TaskList:
                    item.join()
                self.Status = False
                break
        print '[*] Scan completed.'
        return self.UrlList


    def GenPayload(self, Url):
        buf = 'GET /%s HTTP/1.1\n' %(Url).replace(' ', '%20').replace('#', '%23').replace('=', '%3d')
        buf += 'Host: %s\n' %(self.Url if self.Url else '%s:%s' %(self.Addr, self.Port))
        buf += 'User-Agent: Yet another browser\n'
        buf += 'Accept: */*\n'
        buf += 'Referer: w\n'
        buf += 'DNT: 1\n'
        buf += 'Connection: Close\n'
        buf += '\n'
        return buf


    def LoadWordlist(self):
        if not os.path.isfile(self.Wordlist):
            print '[!] Invalid Wordlist file, Using default.'
            mode = raw_input('[*] Wordlist type (s/M/l): ').upper()
            if mode == 'S':
                UrlList = open(self.WordlistDir + '/SmallSensitiveFileList.txt', 'r')
            elif mode == 'L':
                UrlList = open(self.WordlistDir + '/LargeSensitiveFileList.txt', 'r')
            else:
                UrlList = open(self.WordlistDir + '/MediumSensitiveFileList.txt', 'r')
        else:
            UrlList = open(self.Wordlist, 'r')
        return UrlList.read().split('\n')


    def _Scanner(self, Url):
        url = '%s://%s/%s' %(self.Protocol, self.Url, Url)
        sess = socket.socket(2, 1)
        try:
            sess.settimeout(int(self.Timeout))
            sess.connect((self.Url if self.Url else self.Addr, self.Port))
            if self.Protocol == 'https' or self.Port == 443:
                sess = ssl.wrap_socket(sess, keyfile=None, server_side=False, cert_reqs=ssl.CERT_NONE, ssl_version=ssl.PROTOCOL_SSLv23)
            sess.send(self.GenPayload(Url))
            resp = sess.recv(512)
            code = re.findall('HTTP/[\d]{1}\.[\d]{1} (.*)?$', resp, re.M)
            if not code:
                return
            code = code[0].strip('\n').strip('\r')
            if '404 Not Found' not in code:
                print '[+] Got %s on %s.' %(code, url)
                if code not in self.UrlList.keys():
                    self.UrlList[code] = []
                self.UrlList[code].append(url)
            pass
        except socket.timeout:
            print '[*] Timed out fetching %s' %(url)
        except socket.error:
            print '[!] Failed to fetch page: %s' %(url)
        except Exception, e:
            print '[!] Error fetching %s: %s' %(url, str(e))
        return


    def _ThreadChecker(self):
        time.sleep(1)
        while self.Status:
            for item in self.TaskList:
                if not item.isAlive():
                    self.TaskList.remove(item)
                    del item
            pass
        return


    def _Timer(self):
        while self.Status:
            time.sleep(1)
            self.Time += 1
        return


    def _TaskNotifier(self):
        time.sleep(1)
        while self.Status:
            time.sleep(5)
            print '[*] Cost %i second(s), %i thread(s) running, %i URL(s) left.' %(self.Time, len(self.TaskList), self.Queue.qsize())
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
        print ' |    |  ----        `-----------'
        for item in args.keys():
            print ' |    |  %s%s' %(item.ljust(12), args[item])
        print ' |'
        print '[*] Scanner information end.'


def test():
    scanner = Scanner()
    scanner.Url = ''
    scanner.Scan()
